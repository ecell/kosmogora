
schema = {
    "list_models": {
        "httpMethod": "GET",
        "request": {
            "pathParameters" : [],
            "queryParameters": [],
        },
        "responce" : {
            "key": "models", "value_type": "str",
        },
    },
    "list_views" : {
        "httpMethod": "GET",
        "request": {
            "pathParameters" : [],
            "queryParameters": [
                {"id": "model_name", "type": "str" }
            ]
        },
        "responce" : {
            "key": "views", 
            "value_type": "str",
        },
    },
    "list_user_model" : {
        "httpMethod": "GET",
        "request": {
            "pathParameters" : [],
            "queryParameters": [
                {"id": "base_model_name", "type": "str" }
            ]
        },
        "response": {
            "key": "user_models",
            "value_type" : "str"
        }
    },
    "list_reaction_id" : {
        "httpMethod": "GET",
        "request": {
            "pathParameters" : [],
            "queryParameters": [
                {"id": "model_name", "type": "str" }
            ]
        },
        "response": "list[str]",
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
            "value_type": "list[list[str, float]]",
        }
    },

    "save": {
        "httpMethod": "GET",
        "request" : {
            "pathParameters" : [
                {"id": "model_name", "type" : "str"},
                {"id": "author", "type" : "str"},
                {"id": "new_model_name", "type" : "str"},
            ],
            "queryParameters": [
                {"id": "command", "type" : "list[str]"},
                {"id": "view_name", "type" : "str"},
            ]
        }, 
        "responce": {
            "key" : "new_model_name",
            "value_type": "str",
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

