import azure.functions as func
import logging
from openai import AzureOpenAI
import json
import os

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

def place_objects(room_dimensions, objects):
    input_json = {
        "room_dimensions": room_dimensions,
        "objects": objects
    }
    
    # Payload for the request
    with open('prompt.txt', 'r', encoding='utf-8') as file:
        context = file.read()
    prompt="\n\nInput: \n" + ex_input_json + "\n\nOutput: \n" + ex_output_json + "\n\nInput: \n" + json.dumps(input_json) + "\n\nOutput: ",
    
    response = client.chat.completions.create(
        model=os.getenv("AZURE_DEPLOYMENT_MODEL"), 
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": ex_input_json},
            {"role": "assistant", "content": ex_output_json},
            {"role": "user", "content": json.dumps(input_json)}
        ]
    )

    message = response.choices[0].message.content
    return message


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
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
            layout = place_objects([dim_x, dim_y, dim_z], objects)
            return func.HttpResponse(json.dumps(layout), status_code=200)
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