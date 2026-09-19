import azure.functions as func
import logging
from openai import AzureOpenAI
import json
import os
from ratelimit import limits, sleep_and_retry

# Define the rate limit: 10 calls per minute
CALLS = 10
PERIOD = 3600

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# set environment variables before importing any other code
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version=os.getenv("OPENAI_API_VERSION")
)

# Example JSON objects showing the format of the input and output loaded from files
with open('sample_input.json', 'r', encoding='utf-8') as f:
    ex_input_json = f.read().strip('\n')
with open('sample_output.json', 'r', encoding='utf-8') as f:
    ex_output_json = f.read().strip('\n')

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def place_objects(room_dimensions, objects):
    input_json = {
        "room_dimensions": room_dimensions,
        "objects": objects
    }
    
    # Payload for the request
    with open('prompt.txt', 'r', encoding='utf-8') as file:
        context = file.read()
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_MODEL"), 
        max_tokens=1500,  # cap response size to bound per-call cost
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": ex_input_json},
            {"role": "assistant", "content": ex_output_json},
            {"role": "user", "content": json.dumps(input_json)}
        ]
    )

    message = response.choices[0].message.content
    return message


# FUNCTION auth level: callers must supply a valid function/host key (?code=...).
# The public front-end goes through the Cloudflare Worker (furnisher-proxy),
# which holds the key server-side and enforces CORS. This closes the previous
# ANONYMOUS exposure where anyone could burn the Azure OpenAI quota.
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
@app.route(route="furnish")
def Furnish(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        logging.debug(req_body)
        dim_x = req_body.get('room_dimensions', {}).get('dim_x')
        dim_y = req_body.get('room_dimensions', {}).get('dim_y')
        dim_z = req_body.get('room_dimensions', {}).get('dim_z')
        objects = req_body.get('objects')
        if dim_x and dim_y and dim_z and objects:
            # Authoritative input validation — bound the prompt to limit
            # Azure OpenAI token cost, regardless of what the caller sends.
            MAX_OBJECTS = 20
            MAX_STR = 200
            MAX_DIM = 1000
            for name, v in (("dim_x", dim_x), ("dim_y", dim_y), ("dim_z", dim_z)):
                if not isinstance(v, (int, float)) or v <= 0 or v > MAX_DIM:
                    raise ValueError(f"{name} out of range")
            if not isinstance(objects, list) or len(objects) > MAX_OBJECTS:
                raise ValueError(f"Too many objects (max {MAX_OBJECTS})")
            for o in objects:
                if isinstance(o, dict):
                    for val in o.values():
                        if isinstance(val, str) and len(val) > MAX_STR:
                            raise ValueError(f"Field exceeds {MAX_STR} characters")
            layout = place_objects([dim_x, dim_y, dim_z], objects)
            return func.HttpResponse(layout, status_code=200)
        else:
            raise ValueError("Missing required parameters")
    except ValueError as ve:
        logging.error("ValueError: %s", str(ve))
        return func.HttpResponse(
            "This function requires the dimensions of a room to be passed as a query string or in the request body, as parameters dim_x, dim_y, dim_z and a list of objects.",
            status_code=422
        )
    except Exception as e:
        logging.error("Unexpected error: %s", str(e), exc_info=True)
        return func.HttpResponse(
            f"An unexpected error occurred: {str(e)}",
            status_code=500
        )
    finally:
        logging.info('Request processing completed.')