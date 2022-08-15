from fastapi import FastAPI, Response, Query, HTTPException
from obj_manager import ModelViewManager, DataDir
from model_handler2 import ModelHandler2
import os

class XMLResponse(Response):
    media_type = "application/xml"

COMMAND_DELIMITER='|'
ARGUMENT_DELIMITER='#'

app = FastAPI()
object_manager = ModelViewManager()

@app.get("/list_models")
def list_models():
    """Returns the list of available models."""
    model_list = object_manager.list_models()
    return {"models": model_list}


@app.get("/list_views/", responses={404: {'description': 'Model not found'}})
def list_views(model_name: str = Query(None) ):
    """
    Returns available views.
    If the 'model_name' is specified as a query parameter, 
    it returns the views related to the specified model.
    """
    if model_name != None and model_name not in object_manager.list_models():
            raise HTTPException(status_code=404, detail="Model not found")

    view_list = object_manager.list_views(model_name)
    return {"views" : view_list}


@app.get("/open_sbml/{model_name}", response_class=XMLResponse, responses={404: {'description': 'Model not found'}})
def open_sbml(model_name: str):
    if model_name not in object_manager.list_models():
        raise HTTPException(status_code=404, detail="Model not found")
    model_path = object_manager.model_property(model_name)["path"]
    data = None
    with open(model_path, 'r') as f:
        data = f.read()
    return Response(content=data, media_type="application/xml")


@app.get("/get_model_property/{model_name}", responses={404: {'description': 'Model not found'}})
def get_model_property(model_name: str):
    """Returns the model property, such as reference database, version. """
    if model_name not in object_manager.list_models():
        raise HTTPException(status_code=404, detail="Model not found")
    data = object_manager.model_property(model_name)
    return data

@app.get("/open_view/{view_name}", responses={404: {'description': 'View not found'}})
def open_view(view_name: str):
    """Returns the view in .cyjs format"""
    import json
    if view_name not in object_manager.list_views(view_name):
        raise HTTPException(status_code=404, detail="Model not found")
    view_path = object_manager.view_property(view_name)["path"]
    data = None
    with open(view_path, 'r') as f:
        data = json.load(f)
    return data

@app.get("/get_view_property/{view_name}", responses={404: {'description': 'Model not found'}})
def get_view_property(view_name: str):
    """Returns the view property, such as reference database, version. """
    if view_name not in object_manager.list_views():
        raise HTTPException(status_code=404, detail="Model not found")
    data = object_manager.view_property(view_name)
    return data

@app.get("/list_user_model/", responses={404: {'description': 'Model not found'}})
def list_user_modification_models(base_model_name: str = Query(None) ):
    if base_model_name != None and base_model_name not in object_manager.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
    user_model_list = object_manager.list_user_models(base_model_name)
    return {"user_models" : user_model_list}

def process_command(model_handler : ModelHandler2, command : str):
    pass

@app.get("/solve2/{model_name}/", responses={404: {'description': 'Model not found'}})
def solve2(model_name: str, commands : str = Query(None)):
    # First, Check the requested model either base_model or user_model
    model_type = object_manager.check_model_type(model_name)

    # Then, load therequested model.
    model_handler = ModelHandler2() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # If the model-operation commands are submitted, apply the commands
    if commands != None:
        # apply commands
        import urllib.parse
        command_decoded = urllib.parse.unquote_to_bytes(commands).decode()
        print(command_decoded.split(COMMAND_DELIMITER))
        for command_str in command_decoded.split(COMMAND_DELIMITER):
            command = command_str.split(ARGUMENT_DELIMITER)
            print(command)
            model_handler.add_modification_command(command)

    # Do FBA!
    data = model_handler.do_FBA()
    return data

@app.get("/save2/{model_name}/{commands}/{author}/{new_model_name}", responses={404: {'description': 'Model not found'}})
def save2(model_name: str, commands: str, author: str, new_model_name: str):
    print(new_model_name)
    if len(commands) == 0 or len(author) == 0:
        raise 

    # First, Check the requested model either base_model or user_model
    model_type = object_manager.check_model_type(model_name)

    # Then, load therequested model.
    model_handler = ModelHandler2() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
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
    
    new_model_file_basename = "{}.yaml".format(new_model_name)
    new_model_file_path = os.path.join(DataDir, new_model_name )
    model_handler.set_author(author)
    model_handler.set_model_name(new_model_name)
    model_handler.save_user_model(new_model_file_path)
    object_manager.register_model(new_model_name, new_model_file_path, model_handler.get_base_model_name() )
    return {"new_model_name" : new_model_name}


