from fastapi import FastAPI, Response, Query, HTTPException
from obj_manager import ModelViewManager
from model_handler2 import ModelHandler2

class XMLResponse(Response):
    media_type = "application/xml"

COMMAND_DELIMITER='|'
ARGUMENT_DELIMITER='#'

app = FastAPI()
obj_manager = ModelViewManager()

@app.get("/list_models")
def list_models():
    """Returns the list of available models."""
    model_list = obj_manager.models()
    return {"models": model_list}


@app.get("/list_views/", responses={404: {'description': 'Model not found'}})
def list_views(model_name: str = Query(None) ):
    """
    Returns available views.
    If the 'model_name' is specified as a query parameter, 
    it returns the views related to the specified model.
    """
    if model_name != None and model_name not in obj_manager.list_models():
            raise HTTPException(status_code=404, detail="Model not found")

    view_list = obj_manager.list_views(model_name)
    return {"views" : view_list}


@app.get("/open_sbml/{model_name}", response_class=XMLResponse, responses={404: {'description': 'Model not found'}})
def open_sbml(model_name: str):
    if model_name not in obj_manager.list_models():
        raise HTTPException(status_code=404, detail="Model not found")
    model_path = obj_manager.model_property(model_name)["path"]
    data = None
    with open(model_path, 'r') as f:
        data = f.read()
    return Response(content=data, media_type="application/xml")


@app.get("/get_model_property/{model_name}", responses={404: {'description': 'Model not found'}})
def get_model_property(model_name: str):
    """Returns the model property, such as reference database, version. """
    if model_name not in obj_manager.list_models():
        raise HTTPException(status_code=404, detail="Model not found")
    data = obj_manager.model_property(model_name)
    return data

@app.get("/open_view/{view_name}", responses={404: {'description': 'View not found'}})
def open_view(view_name: str):
    """Returns the view in .cyjs format"""
    import json
    if view_name not in obj_manager.list_views(view_name):
        raise HTTPException(status_code=404, detail="Model not found")
    view_path = obj_manager.view_property(view_name)["path"]
    data = None
    with open(view_path, 'r') as f:
        data = json.load(f)
    return data

@app.get("/get_view_property/{view_name}", responses={404: {'description': 'Model not found'}})
def get_view_property(view_name: str):
    """Returns the view property, such as reference database, version. """
    if view_name not in obj_manager.list_views():
        raise HTTPException(status_code=404, detail="Model not found")
    data = obj_manager.view_property(view_name)
    return data

@app.get("/list_user_model/", responses={404: {'description': 'Model not found'}})
def list_user_modification_models(base_model_name: str = Query(None) ):
    if base_model_name != None and base_model_name not in obj_manager.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
    user_model_list = obj_manager.list_user_models(base_model_name)
    return {"user_models" : user_model_list}

def process_command(model_handler : ModelHandler2, command : str):
    pass

@app.get("/solve2/{model_name}/", responses={404: {'description': 'Model not found'}})
def solve2(model_name: str, commands : str = Query(None)):
    model_type = obj_manager.check_model_type(model_name)
    model_handler = ModelHandler2() 
    if model_type == "base_model" :
        model_path = obj_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = obj_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if commands != None:
        # apply commands
        import urllib.parse
        command_decoded = urllib.parse.unquote_to_bytes(commands).decode()
        print(command_decoded.split(COMMAND_DELIMITER))
        for command_str in command_decoded.split(COMMAND_DELIMITER):
            command = command_str.split(ARGUMENT_DELIMITER)
            print(command)
            model_handler.add_modification_command(command)

    data = model_handler.do_FBA()
    return data