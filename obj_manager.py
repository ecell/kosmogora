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
        base_model : str, parent_model_path : Optional[str] = None):
        date_str = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
        meta_data = {
            "path" : user_model_path,
            "base_model" : base_model,
            "parent_model_path" : parent_model_path,
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
            'iJO1366' : {"database_type" : "bigg", "default_view" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.xml" }
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
    if not os.path.exists(MetaInfoDir):
        shutil.rmtree(MetaInfoDir)
    if not os.path.exists(DataDir):
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

    #manager = ModelViewManager()
    #print(manager.list_models() )   # => ['iJO1366', 'sample1']
    #print(manager.list_views() )    # => ['iJO1366', 'sample1']
    #print(manager.list_views("iJO1366"))    # => ['iJO1366']
    #print(manager.list_user_models("iJO1366")) # => []
    #print(manager.model_property("iJO1366"))
    #print(manager.check_model_type("iJO1366"))
    #print(manager.check_model_type("test23"))
    #print(manager.check_model_type("test33"))
