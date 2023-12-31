# Furnish Function App

A POC Azure Function App that uses Azure OpenAI Services to help users place objects within a room.

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

The request body should be a JSON object with the following properties:

| Name | Type | Description |
| --- | --- | --- |
| `room_dimensions` | Object | An object containing the dimensions of the room. |
| `room_dimensions.dim_x` | Number | The length of the room in the x direction. |
| `room_dimensions.dim_y` | Number | The length of the room in the y direction. |
| `room_dimensions.dim_z` | Number | The height of the room. |
| `objects` | Array | An array of objects to place in the room. |
| `objects[].name` | String | The name of the object. |
| `objects[].dimensions` | Object | An object containing the dimensions of the object. |
| `objects[].dimensions.dim_x` | Number | The length of the object in the x direction. |
| `objects[].dimensions.dim_y` | Number | The length of the object in the y direction. |
| `objects[].dimensions.dim_z` | Number | The height of the object. |

Example request body:

```json
{
  "room_dimensions": {
    "dim_x": 10,
    "dim_y": 10,
    "dim_z": 3
  },
  "objects": [
    {
      "name": "Table",
      "dimensions": {
        "dim_x": 2,
        "dim_y": 2,
        "dim_z": 1
      }
    },
    {
      "name": "Chair",
      "dimensions": {
        "dim_x": 1,
        "dim_y": 1,
        "dim_z": 2
      }
    }
  ]
}
```

## Furnish UI

You can use the [Furnish UI](https://yusuf.kaka.co.za/furnish_ui/) project to visualize the layout generated by this function. Source code for the Furnish UI can be found [here](https://github.com/yusufk/furnish_ui)