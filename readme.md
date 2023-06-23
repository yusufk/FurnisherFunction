A POC Azure Function App, that uses Azure OpenAI Services to help users place objects within a room.

## How to use
1. Clone the repo
2. Create a new Azure Function App
3. Create a new Azure OpenAI Service resource
4. Setup a model in the Azure OpenAI Service resource based on davinci-codex
5. Setup environment variables in the Azure Function App
6. Deploy the Azure Function App

## Environment variables
| Name | Description |
| --- | --- |
| OPENAI_API_KEY | The API key for the Azure OpenAI Service resource |
| OPENAI_ENDPOINT | The endpoint for the Azure OpenAI Service resource |

## API
### POST /api/furnish
#### Request
```json
{"dim_x":"10", "dim_y":"10","dim_z":"10","objects": [
    {
        "name": "chair",
        "dimensions": [1, 1, 1]
    },
    {
        "name": "table",
        "dimensions": [2, 2, 2]
    }
]}
```
#### Response
```json
{
    "room_dimensions": [10, 10, 10],
    "objects": [
        {
            "name": "chair",
            "position": [3, 1, 0.5],
            "rotation": [0, 0, 0]
        },
        {
            "name": "table",
            "position": [5, 5, 0.5],
            "rotation": [0, 0, 0]
        }
    ]
}
```
