import azure.functions as func
import logging
import openai
import json
import os

openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example JSON objects showing the format of the input and output loaded from files
with open('sample_input.json', 'r', encoding='utf-8') as f:
    ex_input_json = f.read().strip('\n')
with open('sample_output.json', 'r', encoding='utf-8') as f:
    ex_output_json = f.read().strip('\n')


def place_objects(room_dimensions, objects):
    # Create the input JSON object
    input_json = {
        "room_dimensions": room_dimensions,
        "objects": objects
    }
    # Load prompt from file
    with open('prompt.txt', 'r', encoding='utf-8') as file:
        prompt_pre = file.read()
    # Create a completion
    response = openai.Completion.create(
    engine="davinci3_deployment_model",
    prompt=prompt_pre + "\n\n\
        Input: \n" + ex_input_json + "\n\n\
        Reasoning: The table is the largest object, therefore placing it in the center of the room. The chair is usually placed next to the table. \n\n\
        Output: \n" + ex_output_json + "\n\n\
        Input: \n" + json.dumps(input_json) + "\n\n\
        Reasoning: ",

    temperature=0.89,
    max_tokens=2544,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    best_of=1,
    stop=None)
    # Log the reasoning for the AI's placement of objects
    logging.info(response.choices[0].text)
    # Parse the response, looking for the start and end of the JSON object by looking for the first and last curly braces"
    json_response = json.loads("{"+response.choices[0].text.split("{",1)[1].rsplit("}",1)[0]+"}")
    return json_response

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
        else:
            raise ValueError 
        return func.HttpResponse(json.dumps(layout),status_code=200)
    except ValueError:
        return func.HttpResponse(
             "This function requires the dimensions of a room to be passed as a query string or in the request body, as parameters dim_x, dim_y, dim_z and a list of objects.",
             status_code=422
        )