import azure.functions as func
import logging
from openai import AzureOpenAI
import json
import os
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup Azure Open AI
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint = os.getenv("OPENAI_API_BASE")
    )

# Create an assistant
with open('prompt.txt', 'r', encoding='utf-8') as file:
        context = file.read()
assistant = client.beta.assistants.create(
    name="Jarvis",
    instructions=context,
    tools=[{"type": "code_interpreter"}],
    model=os.getenv("ENGINE")
)

# Start a conversation
conversation = client.beta.threads.create()

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
    prompt="\n\nInput: \n" + ex_input_json + "\n\nOutput: \n" + ex_output_json + "\n\nInput: \n" + json.dumps(input_json) + "\n\nOutput: ",
    
    # Add the user question to the thread
    message = client.beta.threads.messages.create(
        thread_id=conversation.id,
        role="user",
        content=prompt
    )

    # Run the thread
    run = client.beta.threads.runs.create(
    thread_id=conversation.id,
    assistant_id=assistant.id,
    )
    status = run.status

    # Wait till the assistant has responded
    while status not in ["completed", "cancelled", "expired", "failed"]:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=conversation.id,run_id=run.id)
        status = run.status

    messages = client.beta.threads.messages.list(
    thread_id=conversation.id
    )
    message =  messages.data[0].content[0].text.value
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