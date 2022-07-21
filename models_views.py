from datetime import datetime
import default
import yaml

class Models_Views:
    '''
    This class manage the models and views.
    '''
    def __init__(self):
        # This should be loaded from files such as XML and YAML.
        #self.model_set = {
        #    'sample1' : {"database_type" : "kegg", "default_view" : "sample1", "version" : "1.0.0", "organ" : "EColi", "path": "./models/sample1.xml" },
        #    'iJO1366' : {"database_type" : "bigg", "default_view" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.xml" }
        #}
        #self.view_set = {
        #    "sample1" : {"database_type" : "kegg", "model" : "sample1", "version" : "1.0.0", "organ" : "EColi" },
        #    "iJO1366" : {"database_type" : "bigg", "model" : "iJO1366", "version" : "1.0.0", "organ" : "EColi" }
        #}
        self.model_set = self.read_yaml(default.RegisteredModelFile)[default.ModelRootKey]
        self.view_set  = self.read_yaml(default.RegisteredViewFile)[default.ViewRootKey]
        self.user_defined_model_set = self.read_yaml(default.UserDefinedModelFile)[default.UserModelRootKey]

        #validity_hours = 10
        validity_hours = None
        if validity_hours != None:
            current_time = datetime.today()
            temp = dict()
            #temp = set(filter( lambda x: (datetime.strptime(x["date"], "%Y-%m-%d_%H:%M:%S") - current_time).seconds < validity_hours * 3600, self.user_defined_model_set) )
            for key, val in self.user_defined_model_set.items():
                dt = current_time - datetime.strptime(val["date"], "%Y-%m-%d_%H:%M:%S")
                #print("{} - {} \t= {}s ".format( datetime.strptime(val["date"], "%Y-%m-%d_%H:%M:%S" ), current_time, dt.seconds ))
                if dt.seconds <= validity_hours * 3600:
                    print("{} passed".format(val))
                    temp[key] = val
            self.user_defined_model_set = temp
            

    def read_yaml(self, filename: str):
        '''
        Reads yaml file which contain the information of the models and views.
        '''
        with open(filename) as file:
            ret = yaml.safe_load(file)
        return ret

    def models(self):
        '''
        Return the list of the available models.
        The list does not include Models modified by users.
        In order to get the list of the models modified by users, user_defined_models() should be called.
        '''
        return list( self.model_set.keys() )
    
    def model_property(self, model_name: str):
        '''
        Returns the property of the model.
        '''
        if model_name in self.model_set:
            return self.model_set[model_name]
        else:
            return None
    
    def views(self):
        '''
        Return the list of the available views.
        '''
        return list( self.view_set.keys() )

    def view_property(self, view_name: str):
        '''
        Returns the property of the view.
        '''
        if view_name in self.view_set:
            return self.view_set[view_name]
        else:
            return None

    def views_of_model(self, model_name: str):
        '''
        Returns the views, which is related to a queried model.
        '''
        ret_val = []
        for view_name, properties in self.view_set.items():
            if "model" in properties and properties["model"] == model_name:
                ret_val.append(view_name)

        return ret_val
    
    def user_defined_models(self):
        '''
        Return the list of the available models, which is modified by the users.
        '''
        return list(self.user_defined_model_set.keys() )

    def register_model(self, model_name : str , new_model_path : str, author : str ):
        date_str = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
        self.user_defined_model_set[model_name] = {
            "model_path" : new_model_path, 
            "author" : author,
            "date" : date_str,
        }
        with open(default.UserDefinedModelFile, "w") as file:
            yaml.dump({default.UserModelRootKey : self.user_defined_model_set }, file)
