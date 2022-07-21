import yaml
import os

RegisteredModelFile  = "./data/registered_model.yaml"
RegisteredViewFile   = "./data/registered_view.yaml"
UserDefinedModelFile = "./data/user_defined_model.yaml"

ModelRootKey = "models"
ViewRootKey = "views"
UserModelRootKey = "user_models"


if __name__ == '__main__':
        model_set = {
                'sample1' : {"database_type" : "kegg", "default_view" : "sample1", "version" : "1.0.0", "organ" : "EColi", "path": "./models/sample1.xml" },
                'iJO1366' : {"database_type" : "bigg", "default_view" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.xml" }
        }

        view_set = {
                "sample1" : {"database_type" : "kegg", "model" : "sample1", "version" : "1.0.0", "organ" : "EColi", "path": "./models/sample1.cyjs" },
                "iJO1366" : {"database_type" : "bigg", "model" : "iJO1366", "version" : "1.0.0", "organ" : "EColi", "path": "./models/iJO1366.cyjs" }
        }


        with open(RegisteredModelFile, "w") as file:
                yaml.dump({ModelRootKey : model_set}, file)

        with open(RegisteredViewFile, "w") as file:
                yaml.dump({ViewRootKey : view_set}, file)

        if not os.path.isfile(UserDefinedModelFile):
            with open(UserDefinedModelFile, "w") as file:
                    yaml.dump({UserModelRootKey: {}}, file)
        else:
            pass

