import azure.functions as func
import logging
import openai
import json
import os

openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example JSON objects showing the format of the input and output
ex_input_json = {
    "room_dimensions": [10, 10, 10],
    "objects": [
        {
            "name": "chair",
            "dimensions": [1, 1, 1],
        },
        {
            "name": "table",
            "dimensions": [2, 2, 2],
        }
    ]
}
ex_output_json = {
    "room_dimensions": [10, 10, 10],
    "objects": [
        {
            "name": "chair",
            "dimensions": [1, 1, 1],
            "position": [1, 1, 1],
            "rotation": [0, 0, 0]
        },
        {
            "name": "table",
            "dimensions": [2, 2, 2],
            "position": [2, 2, 2],
            "rotation": [0, 0, 0]
        }
    ]
}

def place_objects(room_dimensions, objects):
    # Create the input JSON object
    input_json = {
        "room_dimensions": room_dimensions,
        "objects": objects
    }
    # Create a completion
    response = openai.Completion.create(
    engine="davinci3_deployment_model",
    prompt="This is an interaction between an AI decorator and a human. The AI will help the human by placing decorative items and furniture in a 3D room, of a specified dimension. The AI will place the objects in the room, based on good design principles, logical placement, and an understanding of the items' purpose, specifying their location and orientation and return the placement as a JSON object. \n\n\
        Input: \n" + json.dumps(ex_input_json) + "\n\n\
        Output: \n" + json.dumps(ex_output_json) + "\n\n\
        Input: \n" + json.dumps(input_json) + "\n\n\
        Output: ",

    temperature=0.89,
    max_tokens=2544,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    best_of=1,
    stop=None)
    # Parse the response, looking for the start and end of the JSON object by looking for the first and last curly braces"
    # print(response.choices[0].text.split("{",1)[1].rsplit("}",1)[0])
    json_response = json.loads("{"+response.choices[0].text.split("{",1)[1].rsplit("}",1)[0]+"}")
    return json_response

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)  

@app.route(route="HttpTrigger")
def HttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    dim_x = req.params.get('dim_x')
    dim_y = req.params.get('dim_y')
    dim_z = req.params.get('dim_z')
    if (not dim_x) or (not dim_y) or (not dim_z):
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            dim_x = req_body.get('dim_x')
            dim_y = req_body.get('dim_y')
            dim_z = req_body.get('dim_z')

    if dim_x:
        return func.HttpResponse(f"Hello, you've specified a room of dimensions x={dim_x}, y={dim_y}, z={dim_z}. ")
    else:
        return func.HttpResponse(
             "This function requires the dimensions of a room to be passed as a query string or in the request body, as parameters dim_x, dim_y, dim_z.",
             status_code=200
        )