import os
import openai
import json
import fastapi
import uvicorn
openai.api_type = "azure"
openai.api_base = "https://jarvis-openai.openai.azure.com/"
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

# Expose the function as an API endpoint using FastAPI and uvicorn
app = fastapi.FastAPI()
@app.post("/place_objects")
def place_objects_api(room_dimensions, objects):
    return place_objects(room_dimensions, objects)
    
# Main function to test the object placer
def main():
    # Create a sample room
    room_dimensions = [10, 10, 10]
    # Create a sample list of objects
    objects = [
        {
            "name": "chair",
            "dimensions": [1, 1, 1],
        },
        {
            "name": "table",
            "dimensions": [2, 2, 2],
        }
    ]
    # Place the objects
    layout = place_objects(room_dimensions, objects)
    # Print the layout
    print(layout)


    
# Main function to test the object placer
if __name__ == "__main__":
    #main()
    # Run the API endpoint
    uvicorn.run(app, host="localhost", port=8000)
    
