from fastapi import FastAPI, Response, Query, HTTPException
from obj_manager import ModelViewManager, DataDir
from model_handler import ModelHandler
from typing import Tuple, List, Union
import os
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

class XMLResponse(Response):
    media_type = "application/xml"

ARGUMENT_DELIMITER='-'

app = FastAPI()
object_manager = ModelViewManager()

@app.get("/list_models")
def list_models():
    """Returns the list of available models."""
    model_list = object_manager.list_models()
    return {"models": model_list}

@app.get("/user_model_tree")
def user_model_tree():
    tree = object_manager.get_user_model_tree()
    return {"tree": tree}

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
        raise HTTPException(status_code=404, detail="View not found")
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

@app.get("/open_user_model/{user_model_name}", responses={404: {'description': 'user_model not found'}})
def open_user_modification_models(user_model_name: str):
    """ """
    import yaml 
    if user_model_name not in object_manager.list_user_models():
        raise HTTPException(status_code=404, detail="UserModel not found")
    user_model_path = object_manager.user_model_property(user_model_name)['path']
    data = None
    with open(user_model_path, 'r') as f:
        data = yaml.safe_load(f)
    return data


def generate_edgeID_to_rxnID_map(view_name: str):
    """ convert reactions specified the edgeID to its original name """
    import json
    if view_name not in object_manager.list_views(view_name):
        raise HTTPException(status_code=404, detail="View not found")
    view_path = object_manager.view_property(view_name)["path"]
    edgeID_to_rxnID ={}
    with open(view_path, 'r') as f:
        view = json.load(f)
        for edge in view["elements"]["edges"]:
            edge_id = edge["data"]["id"]
            rxn_id = edge["data"]["bigg_id"]
            edgeID_to_rxnID[edge_id] = rxn_id
    return edgeID_to_rxnID

def get_specified_view_path(view_name: str):
    if view_name not in object_manager.list_views(view_name):
        raise HTTPException(status_code=404, detail="View not found")
    view_path = object_manager.view_property(view_name)["path"]
    return view_path

@app.get("/list_reaction_id", responses={404: {'description': 'Model not found'}} )
def list_reaction_ids(model_name: str):
    model_type = object_manager.check_model_type(model_name)
    model_handler = ModelHandler() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")
    return model_handler.list_reaction_ids()


@app.get("/solve/{model_name}/", responses={404: {'description': 'Model not found'}} )
def solve(model_name: str, command : Union[List[str], None] = Query(default=None), view_name: str = Query(default=None)):
    """ Solve the model.

    Parameters:
    ---
    model_name: model name, such as iJO1366. Both base_model and user_defined_model can be specified.

    command: additional command to modify the model. Details are described below. 

    view_name: If reactions in commands are specified by the edgeID of the view, specify the view.

    About command:
    ---
    The parameter 'command' are used to modify the model for the calculation. 
    Currently, 'knockout' and 'bound' are supported. 
    Command and arguments are separated by '-'(hyphen).  
    
    For example, 'knockout-succ_p' means knockout the reaction named 'succ_p'.
    As another example, 'bound-q8_c-0-2' set the 0 for the lowerer bound and 2 for the upper bound of the reaction q8_c, respectively.

    In order to set the multiple modicications, specify like 'command=knockout-succ_p&command=bound-q8_c-0-2'.
    """
    model_type = object_manager.check_model_type(model_name)
    model_handler = ModelHandler() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")

    # if reactions are specified by the edge-index instead of ID,
    #  make a table to convert them.
    edgeID_to_rxnID = None
    if view_name != None:
        #edgeID_to_rxnID = generate_edgeID_to_rxnID_map(view_name)
        edgeID_to_rxnID = None 
        model_handler.set_id_type( get_specified_view_path(view_name) )

    # If the model-operation commands are submitted, apply the commands
    if command != None:
        for cmd in command:
            tokens = cmd.split(ARGUMENT_DELIMITER)
            print(tokens)
            model_handler.add_modification_command(tokens)
    # Do FBA!
    data = model_handler.do_FBA()
    return data

@app.get("/save/{model_name}/{author}/{new_model_name}", responses={404: {'description': 'Model not found'}})
def save(model_name: str, author: str, new_model_name: str, command: Union[List[str], None] = Query(None),  view_name : str = Query(None) ):
    """ Save user model. Saved models can be shown in by the 'open_user_model' API.

    Parameters:
    ---
    model_name: model name, such as iJO1366. Both base_model and user_defined_model can be specified.

    command: additional command to modify the model. Details are described below. 

    author: author name

    new_model_name: new model name to store.

    view_name: If reactions in commands are specified by the edgeID of the view, specify the view.

    About command:
    ---
    The parameter 'command' are used to modify the model for the calculation. 
    Currently, 'knockout' and 'bound' are supported. 
    Command and arguments are separated by '-'(hyphen).  
    
    For example, 'knockout-succ_p' means knockout the reaction named 'succ_p'.
    As another example, 'bound-q8_c-0-2' set the 0 for the lowerer bound and 2 for the upper bound of the reaction q8_c, respectively.

    In order to set the multiple modicications, specify like 'command=knockout-succ_p&command=bound-q8_c-0-2'.
    """

    # Error check
    if command == None or len(command) == 0:
        raise HTTPException(status_code=500, detail='Both the commands and author must be specified')
    if len(author) == 0:
        raise HTTPException(status_code=500, detail='Both the commands and author must be specified')
    if new_model_name in object_manager.list_user_models():
        raise HTTPException(status_code=500, detail='The name {new_model_name} already exists'.format(new_model_name))

    # First, Check the requested model either base_model or user_model
    model_type = object_manager.check_model_type(model_name)

    # Then, load therequested model.
    model_handler = ModelHandler() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")

    # if the reactions in the argument 'commmands' are specified by the edgeID defined in the view,
    # We have to generate the table.
    edgeID_to_rxnID = None
    if view_name != None:
        #edgeID_to_rxnID = generate_edgeID_to_rxnID_map(view_name)
        edgeID_to_rxnID = None 
        model_handler.set_id_type( get_specified_view_path(view_name) )

    if command != None:
        for cmd in command:
            tokens = cmd.split(ARGUMENT_DELIMITER)
            print(tokens)
            model_handler.add_modification_command(tokens)
    
    new_model_file_basename = "{}.yaml".format(new_model_name)
    new_model_file_path = os.path.join(DataDir, new_model_file_basename )
    model_handler.set_author(author)
    model_handler.set_model_name(new_model_name)
    model_handler.save_user_model(new_model_file_path)
    object_manager.register_model(new_model_name, new_model_file_path, model_handler.get_base_model_name(), model_name )
    return {"new_model_name" : new_model_name}

@app.get("/metabolite_information/{model_name}/{metabolite_id}")
def get_metabolite_info(model_name: str, metabolite_id: str, view_name: str = Query(None) ):
    """Get the information of the metabolite. 

    Currently, only 'bigg' is supported.

    Parameters:
    ---
    model_name: model name, such as iJO1366. Both base_model and user_defined_model can be specified.

    metabolite_id: metabolite name such as nadh_c

    view_name: If the view file (such as iJO1366) is set, the 'metabolite_id' parameter can be set with the index of the metabolite instead of its name.
    """
    model_type = object_manager.check_model_type(model_name)
    model_handler = ModelHandler() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")
    if view_name != None:
        model_handler.set_id_type( get_specified_view_path(view_name) )
    model_property = object_manager.model_property(model_name)
    if model_property is not None:
        if "metabolites_db" in model_property:
            metabolite_db = model_property["metabolites_db"]
            metabolite_info = model_handler.get_metabolite_information(metabolite_db, metabolite_id)
            if metabolite_info != {}:
                return {"metabolite_information": metabolite_info }
            else:
                raise HTTPException(
                        status_code=404, detail="metabolite name is not defined in the db".format(model_name))
    else:
        raise HTTPException(status_code=404, detail="Model not found")


@app.get("/reaction_information/{model_name}/{reaction_id}")
def get_reaction_info(model_name: str, reaction_id: str, 
        db_src: str = Query(None), view_name: str = Query(None)):
    """Get the information of the reaction. db_src can be set 'bigg' or 'metanetx'.

    Parameters:
    ---
    model_name: model name, such as iJO1366. Both base_model and user_defined_model can be specified.

    reaction_id: reaction name such as MDH

    db_src: database source. Currently, 'bigg' or 'metanetx' can be set.

    view_name: If the view file (such as iJO1366) is set, the 'reaction_name' parameter  can be set with the index of the reaction instead of its name.
    """

    import information
    model_type = object_manager.check_model_type(model_name)
    model_handler = ModelHandler() 
    if model_type == "base_model" :
        model_path = object_manager.model_property(model_name)["path"]
        model_handler.set_base_model(model_name, model_path)
    elif model_type == "user_model":
        model_path = object_manager.user_model_property(model_name)["path"]
        model_handler.load_user_model(model_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")

    # First, get the name of the reaction from the model file.
    if view_name != None:
        model_handler.set_id_type( get_specified_view_path(view_name) )
        reaction_id = model_handler.get_reaction_name(reaction_id)

    model_property = object_manager.model_property(model_name)
    # Get the database type of the model
    model_db_type = None
    if model_property != None and "reaction_db" in model_property:
        model_db_type = model_property["database_type"]

    # DB source specified by user
    if db_src == None:
        db_src = model_db_type  # default value

    db_table = {
        "bigg" : "bigg.reaction", "metanetx" : "metanetx.reaction",
    }
    if model_db_type in db_table:   
        # ex) bigg => bigg.reaction
        model_db_type = db_table[model_db_type]
    else:
        raise HTTPException(status_code=404, detail="Model DB not found")

    if db_src in db_table:
        db_src = db_table[db_src]
    else:
        raise HTTPException(status_code=404, detail="Specified DB not found")

    if model_db_type != db_src:
        reaction_id = information.convert_name(model_db_type, reaction_id, db_src)

    ret = None
    if reaction_id != None:
        ret = information.get_reaction_information(reaction_id, db_src)
    if ret != None:
        return { "reaction_information": ret }
    else:
        raise HTTPException(status_code=404, detail="Reaction {} not found at {}".format(reaction_id, db_src))


@app.get("/modules")
def get_module_information():
    return {"modules": ["FBA"]}

@app.get("/apis/")
def get_api_information(api_id: str = Query(None)):
    import api_definition
    import json
    if api_id == None:
        api_list = [
            "list_models", 
            "user_model_tree", 
            "list_views", 
            "open_sbml", 
            "open_sbml", 
            "get_model_property", 
            "open_view",
            "get_view_property",
            "list_user_model",
            "open_user_model",
            "list_reaction_id",
            "solve",
            "save",
            "metabolite_information",
            "reaction_information",
        ]
        s = {"apis" : api_list} 
        return JSONResponse(content = s)
    else:
        if api_id in api_definition.schema:
            s = json.dumps( api_definition.schema[api_id] )
            return JSONResponse(content = s)
        else:
            return None
