from xmlrpc.client import Boolean
from fastapi import FastAPI, Query, Body, Response, HTTPException

from typing import Optional
import json
import cobra.io
from logging import getLogger
from models_views import Models_Views
from model_handler import ModelHandler

#logger = getLogger(__name__)
logger = getLogger('uvicorn')

class XMLResponse(Response):
    media_type = "application/xml"


app = FastAPI()
models_views = Models_Views()

def open_model(model_name: str, view_path: Optional[str] = None):
    """ 
    Opens the model and return the ModelHandler object.
    The model_name is either raw model or user_defined model.
    """
    import os
    usermodel_path = f"user_defined_model/{model_name}.yaml"      
    model_handler = ModelHandler()

    if model_name in models_views.models(): # case 1: Base Model
        model_path = models_views.model_property(model_name)["path"]
        model_handler.load_model(model_path)
        if view_path != None:
            model_handler.set_view_file(view_path)
    elif os.path.isfile(usermodel_path):   # case 2: User defined model
        model_handler.load_user_model(usermodel_path)
    else:   # Error
        model_handler = None
    return model_handler


@app.get("/list_models")
def list_models():
    """Returns the list of available models."""
    model_list = models_views.models()
    return {"models": model_list}

@app.get("/list_views/{model_name}", responses={404: {'description': 'Model not found'}})
def list_views(model_name: str):
    """Returns available views related to the queried model"""
    if model_name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")
    return {"views": models_views.views_of_model(model_name)}


@app.get("/open_sbml/{name}", response_class=XMLResponse, responses={404: {'description': 'Model not found'}})
def open_sbml(name: str):
    """Returns the model, written in XML format. """
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")

    model_path = models_views.model_property(name)["path"]
    with open(model_path, 'r') as f:
        data = f.read()
    return Response(content=data, media_type="application/xml")

@app.get("/model/{name}", responses={404: {'description': 'Model not found'}}, deprecated=True)
def model(name: str):
    # XXX This function originally should responce model, instead of *.cyjs.
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")

    view_path = models_views.view_property(name)["path"]
    with open(view_path, 'r') as f:
        data = json.load(f)
    return data

@app.get("/get_model_property/{name}", responses={404: {'description': 'Model not found'}})
def get_model_property(name: str):
    """Returns the model property, such as reference database, version. """
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")
    data = models_views.model_property(name)
    return data

@app.get("/open_view/{name}", responses={404: {'description': 'Model not found'}})
def open_view(name: str):
    """Returns the view in .cyjs format"""
    if name not in models_views.views_of_model(name):
        raise HTTPException(status_code=404, detail="Model not found")

    view_path = models_views.view_property(name)["path"]
    with open(view_path, 'r') as f:
        data = json.load(f)
    return data

@app.get("/get_view_property/{name}", responses={404: {'description': 'Model not found'}})
def get_view_property(name: str):
    """Returns the view property, such as reference database, version. """
    if name not in models_views.views():
        raise HTTPException(status_code=404, detail="Model not found")
    data = models_views.view_property(name)
    return data

def make_time_string():
    import datetime
    now = datetime.datetime.now()
    d = '{:%Y%m%d%H%M}'.format(now)
    return d

@app.get("/solve/{name}", responses={404: {'description': 'Model not found'}}, deprecated=True)
def solve(name: str, knockouts: str = Query(None)):
    """ Execute the flux balance analysis (FBA) """
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")

    if knockouts is None:
        knockouts = []
    else:
        knockouts = knockouts.split(',')
        logger.warning(f'Solve {name} model with {len(knockouts)} knowkout')

    model_path = models_views.model_property(name)["path"]
    model = cobra.io.read_sbml_model(model_path)

    with model:
        for reaction_id in knockouts:
            if not model.reactions.has_id(reaction_id):
                logger.warn(f'Reaction [{reaction_id}] not found.')
                continue

            model.reactions.get_by_id(reaction_id).knock_out()
        solution = model.optimize()

    data = {
        'fluxes': sorted(solution.fluxes.items(), key=lambda kv: kv[0]),
        'objective_value': solution.objective_value}
    return data


@app.get("/save_model/{new_model_name}/{base_model_name}/", responses={404: {'description': 'Model not found'}})
def save_model(new_model_name: str, base_model_name: str, modification: str = Query(None), author = Query(None), description = Query(None), view_name = Query(None)):
    """
    Save user defined model.
    For the base_model_name, both prepared model and other user-defined model can be specified.
    """
    view_path = None
    if view_name != None:
        if view_name in models_views.views_of_model(base_model_name):
            view_path = models_views.view_property(view_name)["path"]
        #view_path = f'./models/{view_name}.cyjs'
    model_handler = open_model(base_model_name, view_path)
    if not isinstance(model_handler, ModelHandler):
        raise HTTPException(status_code=404, detail="Model not found")

    if modification != None:
        model_handler.edit_model_by_query_str(modification)
    
    outfile_path = f"user_defined_model/{new_model_name}.yaml"
    model_handler.save_user_model(outfile_path, author, description)
    models_views.register_model(new_model_name, outfile_path, author)
    return new_model_name

@app.get("/list_user_model/", responses={404: {'description': 'Model not found'}})
def list_user_defined_models():
    """
    Get the list of the user defined models.
    """
    model_list = models_views.user_defined_models()
    return {"user_defined_models": model_list}


@app.get("/solve2/{name}/", responses={404: {'description': 'Model not found'}})
def solve2(name: str, modification : str = Query(None), view_name : str = Query(None) ):
    view_path = None
    if view_name != None:
        view_path = models_views.view_property(view_name)["path"]
    model_handler = open_model(name, view_path)
    if not isinstance(model_handler, ModelHandler):
        raise HTTPException(status_code=404, detail="Model not found")

    if modification != None:
        result= model_handler.edit_model_by_query_str(modification)
        print(f"model edit: {result}")

    solution = model_handler.solve()
    return solution

@app.get("/get_user_modification/{user_model_name}/", responses={404: {'description': 'Model not found'}})
def get_user_modification(user_model_name: str):
    '''
    Returns the modifications of the specified user-defined model;
    '''
    import os
    user_model_path = f"user_defined_model/{user_model_name}.yaml"      
    if os.path.isfile(user_model_path):  
        with open(user_model_path) as file:
            return yaml.safe_load(file)
    else:
        raise HTTPException(status_code=404, detail="Model not found")

# @app.get("/hello")
# def hello():
#    return {"Hello": "World!"}
# 
# @app.post("/users/{name}")
# def create_user(name: str, age: int = Query(None), body: dict = Body(None)):
#     return {
#         "age": age,
#         "name": name,
#         "country": body["country"],
#     }
