import azure.functions as func
import logging
from openai import AzureOpenAI
import json
import os

client = AzureOpenAI(
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_version="2022-12-01",
    api_key=os.getenv("OPENAI_API_KEY")
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
    with open('prompt.txt', 'r', encoding='utf-8') as file:
        prompt_pre = file.read()
    try:
        response = client.completions.create(
            model=os.getenv("OPENAI_ENGINE"),
            prompt=prompt_pre + "\n\nInput: \n" + ex_input_json + "\n\nOutput: \n" + ex_output_json + "\n\nInput: \n" + json.dumps(input_json) + "\n\nOutput: ",
            temperature=0.2,
            max_tokens=2544,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            best_of=1,
            stop=None
        )
        logging.info("OpenAI API response: %s", response.choices[0].text)
        json_response = json.loads("{" + response.choices[0].text.split("{", 1)[1].rsplit("}", 1)[0] + "}")
        return json_response
    except Exception as e:
        logging.error("Error in place_objects: %s", str(e))
        raise

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
        logging.error("Unexpected error: %s", str(e))
        return func.HttpResponse(
            f"An unexpected error occurred: {str(e)}",
            status_code=500
        )
