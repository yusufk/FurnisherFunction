import azure.functions as func
import logging
from openai import AzureOpenAI
import json
import os
import requests

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT = os.getenv("OPENAI_ENDPOINT")
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

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

    # Payload for the request
    prompt=prompt_pre + "\n\nInput: \n" + ex_input_json + "\n\nOutput: \n" + ex_output_json + "\n\nInput: \n" + json.dumps(input_json) + "\n\nOutput: ",
    payload = {
    "messages": [
        {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": prompt
            }
        ]
        }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 4096
    }

    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")
    
    # Parse the response to extract the correct JSON payload
    json_response = response.json()
    for message in json_response:
        if message['role'] == 'assistant':
            return message['content'][0]['text']
    
    raise ValueError("No valid response from assistant")


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