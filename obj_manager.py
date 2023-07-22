from typing import Optional
from datetime import datetime
import yaml
import os

DataDir = "./data2/"
MetaInfoDir = "./manager2/"

#BaseModelList = "./manager/base_model_list.yaml"
#ViewList = "./manager/view_list.yaml"
#UserModificationList = "./manager/modifications_list.yaml"

BaseModelList = os.path.join(MetaInfoDir, "base_model_list.yaml")
ViewList = os.path.join(MetaInfoDir, "view_list.yaml")
UserModificationList = os.path.join(MetaInfoDir, "modifications_list.yaml")

ModelRootKey = "models"
ViewRootKey = "views"
UserModelRootKey = "user_models"

class ModelViewManager:
    def __init__(self):
        self.base_model_set = self.load_yaml(BaseModelList)[ModelRootKey]
        self.view_set = self.load_yaml(ViewList)[ViewRootKey]
        self.user_model_set = self.load_yaml(UserModificationList)[UserModelRootKey]
        pass

    def load_yaml(self, filename: str):
        with open(filename) as file:
            ret = yaml.safe_load(file)
        return ret
    
    def list_models(self):
        return list(self.base_model_set.keys() )

    def get_user_model_tree(self):
        tree = {}
        for model_name, model_property in self.user_model_set.items():
            parent_model = model_property["parent_model"]
            if not parent_model in tree:
                tree[parent_model] = set()
            tree[parent_model].add(model_name)
        return tree

    def model_property(self, model_name : str):
        if model_name in self.base_model_set:
            return self.base_model_set[model_name]
        else:
            return None

    def list_views(self, model_name : Optional[str] = None):
        if model_name != None:
            ret = []
            for name, property in self.view_set.items():
                if property["model"] == model_name:
                    ret.append(name)
            return ret
        else:
            return list(self.view_set.keys() )

    def view_property(self, view_name: str):
        if view_name in self.view_set:
            return self.view_set[view_name]
        else:
            return None

    def list_user_models(self, base_model_name : Optional[str] = None): 
        if base_model_name != None:
            ret = []
            for name, property in self.user_model_set.items():
                if property["base_model"] == base_model_name:
                    ret.append(name)
            return ret
        else:
            return ( list(self.user_model_set.keys()) )

    def user_model_property(self, user_model_name : str):
        if user_model_name in self.user_model_set:
            return self.user_model_set[user_model_name]
        else:
            return None


    def check_model_type(self, model_name : str):
        '''
        check the given model_name  is weather registere_model or user_model.
        return value:
            "base_model", "user_model", None (not exist)
        '''
        if model_name in self.base_model_set:
            return "base_model"
        elif model_name in self.user_model_set:
            return "user_model"
        else:
            return None

    def register_model(self, user_model_name : str, user_model_path : str, 
        base_model : str, parent_model: str):
        date_str = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
        meta_data = {
            "path" : user_model_path,
            "base_model" : base_model,
            "parent_model" : parent_model,
            "date" : date_str
        }
        self.user_model_set[user_model_name] = meta_data
        print("ok save")
        with open(UserModificationList, "w") as file:
            yaml.dump( {UserModelRootKey: self.user_model_set}, file )

def initialize():
    if not os.path.exists(MetaInfoDir):
        os.mkdir(MetaInfoDir)
    if not os.path.exists(DataDir):
        os.mkdir(DataDir)

    model_set = {
            'sample1' : {"database_type" : "kegg", "default_view" : "sample1", "version" : "1.0.0", "organ" : "EColi", "path": "./models/sample1.xml" },
            'iJO1366' : {"database_type" : "bigg", "default_view" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.xml", 
                "reaction_db": "./models/bigg_models_reactions.txt", 
                "metabolites_db": "./models/bigg_models_metabolites.txt"   }
    }
    view_set = {
            "sample1" : {"database_type" : "kegg", "model" : "sample1", "version" : "1.0.0", "organ" : "EColi", "path": "./models/sample1.cyjs" },
            "iJO1366" : {"database_type" : "bigg", "model" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.cyjs" }
    }
    if not os.path.isfile(BaseModelList):
        with open(BaseModelList, "w") as file:
                yaml.dump({ModelRootKey : model_set}, file)

    if not os.path.isfile(ViewList):
        with open(ViewList, "w") as file:
                yaml.dump({ViewRootKey : view_set}, file)

    if not os.path.isfile(UserModificationList):
        with open(UserModificationList, "w") as file:
                yaml.dump({UserModelRootKey: {}}, file)
    else:
        pass

def _cleanup():
    import shutil
    if os.path.exists(MetaInfoDir):
        shutil.rmtree(MetaInfoDir)
    if os.path.exists(DataDir):
        shutil.rmtree(DataDir)


if __name__ == '__main__':
    import sys
    if 2 <= len(sys.argv):
        if sys.argv[1] == '-c':
            print("clean up {} and {}".format(DataDir, MetaInfoDir))
            _cleanup()
            initialize()
    else:
        print("If you specify the option '-c', it will clean all the user_defined models and reset. ")

