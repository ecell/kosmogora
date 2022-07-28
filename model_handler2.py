import json
import cobra.io
from typing import Optional, List, Dict

class ModelHandler2:
    def __init__(self, base_model_name : Optional[str] = None, base_model_path: Optional[str] = None):
        self.base_model_name = base_model_name
        self.base_model_path = base_model_path
        self.model_path = None  # The file of this pass is user_model.
        self.model_name = None
        self.model = None

        self.modification_list = [] # Modifications, defined in the defined by users previously.
        self.new_modifications = []
        self.author = None
        pass

    def set_base_model(self, base_model_name : str, base_model_path : str):
        self.base_model_name = base_model_name 
        self.base_model_path = base_model_path

    def get_base_model_name(self) -> str:
        assert self.base_model_name != None 
        return self.base_model_name 

    def add_modification_command(self, command : List[str]):
        self.new_modifications.append(command)
    
    def add_modification_set(self, modification : Dict ):
        self.modification_list.append(modification)
    
    def get_modification_set(self):
        return self.modification_list
    
    def set_author(self, author_name : str):
        self.author = author_name
    
    def set_model_name(self, model_name : str):
        self.model_name = model_name

    def save_user_model(self, user_model_path : str):
        import yaml
        from datetime import datetime
        if self.author == None:
            raise "Author is required. Please set the author by calling set_author()"
        if len(self.new_modifications) == 0:
            raise "There are no new modification!"
        date_str = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
        temp_modification = {
            "author" : self.author,
            "commands" : self.new_modifications,
            "date" : date_str
        }
        self.modification_list.append(temp_modification)
        data = {
            "base_model_name" : self.base_model_name,
            "base_model_path" : self.base_model_path,
            "model_name" : self.model_name,
            "modification_list" : self.modification_list
        }
        with open(user_model_path, "w") as file:
            yaml.dump(data, file)

    def load_user_model(self, user_model_path : str):
        self.model_path = user_model_path
        import yaml 
        user_defined_data = dict()
        with open(user_model_path) as file:
            user_defined_data = yaml.safe_load(file)
        assert "base_model_path" in user_defined_data
        assert "base_model_name" in user_defined_data 
        assert "model_name" in user_defined_data
        assert "modification_list" in user_defined_data
        self.base_model_name = user_defined_data["base_model_name"]
        self.base_model_path = user_defined_data["base_model_path"]
        self.modification_list = user_defined_data["modification_list"]
        self.model_name = user_defined_data["model_name"]

    def _apply_modification(self, modification_commands):
        if self.model == None:
            raise

        for command in modification_commands:
            if command[0] == "knockout":
                reaction_id = command[1]
                if self.model.reactions.has_id(reaction_id):
                    self.model.reactions.get_by_id(reaction_id).knock_out()
            elif command[0] == "bound":
                reaction_id = command[1]
                lower_bound = command[2]
                upper_bound = command[3]
                if self.model.reactions.has_id(reaction_id):
                    self.model.reactions.get_by_id(reaction_id).bounds = (lower_bound, upper_bound)
            else:
                #raise "Unknown command"
                pass
        
    def do_FBA(self):
        # First, load the original model
        self.model = cobra.io.read_sbml_model(self.base_model_path)

        # second, apply the previously defined commands.
        for modification in self.modification_list:
            self._apply_modification(modification["commands"])
        
        # Third, apply the current commands
        self._apply_modification(self.new_modifications)

        with self.model:
            solution = self.model.optimize()

        data = {
            'fluxes': sorted(solution.fluxes.items(), key=lambda kv: kv[0]),
            'objective_value': solution.objective_value}

        return data

if __name__ == '__main__':
    mh = ModelHandler2("iJO1366", "./models/iJO1366.xml")
    # Originally, this function should by called by user.
    # This function should be called internally in load_user_model().(NOT called directry by users.)
    mh.add_modification_set({
        "author": "sakamoto", 
        "commands" : [
            ["bound", "DHPPD", 0.01, 0.5], 
            ["knockout", "DHAtex"]
            ]} 
            )
    print(mh.get_modification_set() )
    #print(mh.do_FBA() )
    mh.add_modification_command(["knockout", "DHAtex"])
    print("hoger")
    mh.set_author("James")
    mh.set_model_name("testtest")
    mh.save_user_model("test222.yaml")
    
    mh2 = ModelHandler2()
    mh2.load_user_model("test222.yaml")
    print(mh2.get_modification_set())
    #print(mh2.do_FBA())
    pass
