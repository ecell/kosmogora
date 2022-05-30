from xmlrpc.client import Boolean
from fastapi import FastAPI, Query, Body, Response, HTTPException

from typing import Optional
import json
import cobra.io
from logging import getLogger
#logger = getLogger(__name__)
logger = getLogger('uvicorn')

#MODELS = ['sample1', 'iJO1366']
class Models_Views:
    def __init__(self):
        # This should be loaded from files such as XML and YAML.
        self.model_set = {
            'sample1' : {"database_type" : "kegg", "default_view" : "sample1", "version" : "1.0.0", "organ" : "EColi", "path": "./models/sample1.xml" },
            'iJO1366' : {"database_type" : "bigg", "default_view" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.xml" }
        }
        self.view_set = {
            "sample1" : {"database_type" : "kegg", "model" : "sample1", "version" : "1.0.0", "organ" : "EColi" },
            "iJO1366" : {"database_type" : "bigg", "model" : "iJO1366", "version" : "1.0.0", "organ" : "EColi" }
        }

    def models(self):
        return list( self.model_set.keys() )
    
    def model_property(self, model_name: str):
        if model_name in self.model_set:
            return self.model_set[model_name]
        else:
            return None
    
    def views(self):
        return list( self.view_set.keys() )

    def view_property(self, view_name: str):
        if view_name in self.view_set:
            return self.view_set[view_name]
        else:
            return None

    def views_of_model(self, model_name: str):
        #return self.views[model_name]
        ret_val = []
        for view_name, properties in self.view_set.items():
            if "model" in properties and properties["model"] == model_name:
                ret_val.append(view_name)

        return ret_val

class XMLResponse(Response):
    media_type = "application/xml"


app = FastAPI()
models_views = Models_Views()

class ModelHandler:
    def __init__(self, base_filename : Optional[str] = None):
        self.base_filename = base_filename
        self.applied_commands = []
        self.num_modified = 0   # the number of the applied modification
        self.model = None

        if base_filename != None:
            self.load_model(base_filename)

    def load_model(self, base_filename: str) -> None:
        self.base_filename = base_filename
        self.model = cobra.io.read_sbml_model(base_filename)

    def load_user_model(self, usermodel_path: str) -> None :
        import yaml 
        user_defined_data = dict()
        with open(usermodel_path) as file:
            user_defined_data = yaml.safe_load(file)

        assert "base_model" in user_defined_data
        assert "modification" in user_defined_data
        self.load_model(user_defined_data["base_model"])
        self.edit_model_by_query_str(user_defined_data["modification"])
    
    def save_user_model(self, outfile_path: str, author : str, description : str) -> None :
        import yaml
        data = {
            "base_model" : self.base_filename,
            "modification" : ','.join(self.applied_commands) ,
            "author" : author,
            "description" : description
        }   
        with open(outfile_path, "w") as file:
            yaml.dump(data, file)


    def apply_bounds(self, reaction_id : str, lower_bound: float, upper_bound : float) -> bool:
        assert self.model != None
        ret_flag = False
        if self.model.reactions.has_id(reaction_id):
            self.model.reactions.get_by_id(reaction_id).bounds = (lower_bound, upper_bound)
            self.num_modified += 1
            ret_flag = True 
        return ret_flag
            
    def apply_knockout(self, reaction_id: str) -> bool :
        assert self.model != None
        ret_flag = False
        if self.model.reactions.has_id(reaction_id):
            self.model.reactions.get_by_id(reaction_id).knock_out()
            self.num_modified += 1
            ret_flag = True 
        return ret_flag

    def edit_model_by_query_str(self, commands: str = None) -> int:
        if commands == None:
            commands = []
        else:
            commands = commands.split(',')
            
        print(commands)
        for cmd in commands:
            cmd = cmd.split('_')
            if cmd[0] == "bound":
                assert len(cmd) == 4
                reaction_id = cmd[1]
                lower_bound, upper_bound = float(cmd[2]), float(cmd[3])
                result = self.apply_bounds(reaction_id, lower_bound, upper_bound)
                if result != True:
                    raise Exception("apply bound failure")

            elif cmd[0] == "knockout":
                assert len(cmd) == 2
                reaction_id = cmd[1]
                result = self.apply_knockout(reaction_id)
                if result != True:
                    raise Exception("apply knockout failure")
        self.applied_commands += commands    

        return self.num_applied_modification()

    def solve(self):
        assert self.model != None
        with self.model:
            solution = self.model.optimize()

        data = {
            'fluxes': sorted(solution.fluxes.items(), key=lambda kv: kv[0]),
            'objective_value': solution.objective_value}

        return data

    def num_applied_modification(self) -> int:
        return self.num_modified


@app.get("/models")
def models():
    """Returns the list of available models."""
    model_list = models_views.models()
    return {"models": model_list}

@app.get("/views/{model_name}", responses={404: {'description': 'Model not found'}})
def views(model_name: str):
    """Returns available views related to the queried model"""
    if model_name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")
    return {"views": models_views.views_of_model(model_name)}


@app.get("/sbml/{name}", response_class=XMLResponse, responses={404: {'description': 'Model not found'}})
def sbml(name: str):
    """Returns the model, written in XML format. """
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")

    with open(f'./models/{name}.xml', 'r') as f:
        data = f.read()
    return Response(content=data, media_type="application/xml")

@app.get("/model/{name}", responses={404: {'description': 'Model not found'}}, deprecated=True)
def model(name: str):
    # XXX This function originally should responce model, instead of *.cyjs.
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")

    with open(f'./models/{name}.cyjs', 'r') as f:
        data = json.load(f)
    return data

@app.get("/model_property/{name}", responses={404: {'description': 'Model not found'}})
def model_property(name: str):
    """Returns the model property, such as reference database, version. """
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")
    data = models_views.model_property(name)
    return data

@app.get("/view/{name}", responses={404: {'description': 'Model not found'}})
def view(name: str):
    """Returns the view in .cyjs format"""
    if name not in models_views.views_of_model(name):
        raise HTTPException(status_code=404, detail="Model not found")

    with open(f'./models/{name}.cyjs', 'r') as f:
        data = json.load(f)
    return data

@app.get("/view_property/{name}", responses={404: {'description': 'Model not found'}})
def view_property(name: str):
    """Returns the view property, such as reference database, version. """
    if name not in models_views.views():
        raise HTTPException(status_code=404, detail="Model not found")
    data = models_views.view_property(name)
    return data

def make_time_string():
    import datetime
    now = datetime.datetime.now()
    d = '{:%Y%m%d%H%M%S}'.format(now)
    return d

@app.get("/edit/{name}/{commands}", responses={404: {'description': 'Model not found'}}, deprecated=True)
def edit_model(name: str, commands : str):
    """Edit model by and save."""
    if name not in models_views.models():
        raise HTTPException(status_code=404, detail="Model not found")

    # First, Open the existence model
    model_path = models_views.model_property(name)["path"]
    model = cobra.io.read_sbml_model(model_path)
    model_hanlder = ModelHandler(model_path)

    if commands is None:
        commands = []
    commands = commands.split(',')
    for cmd in commands:
        cmd = cmd.split('_')
        print(cmd)
        # BOUNDARY
        if cmd[0] == 'bound':
            print("bound")
            if len(cmd) != 4:
                raise HTTPException(status_code=404, detail="Invalid command")
            reaction_id = cmd[1]
            lower_bound = float(cmd[2])
            upper_bound = float(cmd[3])
            result = model_hanlder.bounds(reaction_id, lower_bound, upper_bound)
            if result != True:
                print(f"Fail: {cmd}")

        elif cmd[0] == 'knockout':
            print("knockcout")
            if len(cmd) != 2:
                raise HTTPException(status_code=404, detail="Invalid command")
            reaction_id = cmd[1]
            result = model_hanlder.knockout(reaction_id)
            if result != True:
                print(f"Fail: {cmd}")

        else:
            #raise HTTPException(status_code=404, detail=f"Unknown command: {cmd[0]}")
            logger.warn(f'Unknown command: {cmd[0]}')
            modified_flag = False

    applied_modification = model_hanlder.num_applied_modification()
    if 0 < applied_modification:
        modified_model_name = f'{model}_{make_time_string()}'
        model_hanlder.save_model(f'./temporary/{modified_model_name}.xml')
        print(modified_model_name)
        return (True, modified_model_name)
    else:
        return (False)

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


@app.get("/save_model/{name}/", responses={404: {'description': 'Model not found'}})
def save_model(name: str, modification: str = Query(None), author = Query(None), description = Query(None)):
    import yaml
    model_path = None
    if name in models_views.models():
        model_path = models_views.model_property(name)["path"]
    else:
        raise HTTPException(status_code=404, detail="Model not found")

    model_handler = ModelHandler(model_path)
    model_handler.edit_model_by_query_str(modification)
    
    outfile_basename = f"{name}_{make_time_string()}"
    outfile_path = f"user_defined_model/{outfile_basename}.yaml"      
    model_handler.save_user_model(outfile_path, author, description)
    return outfile_basename

@app.get("/solve3/{name}/", responses={404: {'description': 'Model not found'}})
def solve3(name: str, modification : str = Query(None) ):
    import os,yaml
    model_path = None
    usermodel_path = f"user_defined_model/{name}.yaml"      

    model_handler = ModelHandler()
    # check whether user defined model, or raw model
    if name in models_views.models():
        model_path = models_views.model_property(name)["path"]
        model_handler.load_model(model_path)
    elif os.path.isfile(usermodel_path):
        model_handler.load_user_model(usermodel_path)
    else:
        raise HTTPException(status_code=404, detail="Model not found")

    if modification != None:
        result= model_handler.edit_model_by_query_str(modification)
        print(f"model edit: {result}")

    solution = model_handler.solve()
    return solution

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
