
schema = {
    "list_models": {
        "httpMethod": "GET",
        "request": {
            "pathParameters" : [],
            "queryParameters": [],
        },
        "responce" : {
            "key": "models", "value": "modelList",
        },
    },

    "solve": {
        "httpMethod": "GET",
        "request" : {
            "pathParameters" : [
                {"id": "modelName", "type" : "str"}
            ],
            "queryParameters": [
                {"id": "command", "type" : "list[str]"},
                {"id": "view_name", "type" : "str"},
            ]
        }, 
        "responce": {
            "key" : "fluxes",
            "value": "list[list[reaction_id, flux]]",
        }
    },

    "reaction_information" : {
        "httpMethod": "GET",
        "request" : {
            "pathParameters" : [
                {"id" : "model_name", "type" : "str"},
                {"id" : "reaction_id", "type" : "str"}
            ],
            "queryParameters" : [
                {"id" : "db_src", "type" : "str"},
                {"id" : "view_name", "type" : "str"},
            ]
        },
        "response": {
            "key" : "reaction_information",
            "value" : {
                "ID" : "reaction_id" ,
                "NAME" : "reaction_name" ,
                "REACTION" : "reaction_expression" ,
                "MODEL_LIST" : "model_list" ,
            }
        }
    }
}

