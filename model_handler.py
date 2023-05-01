import json
import cobra.io
from typing import Optional, List, Dict

class ModelHandler:
    def __init__(self, base_model_name : Optional[str] = None, base_model_path: Optional[str] = None):
        self.base_model_name = base_model_name
        self.base_model_path = base_model_path
        self.model_path = None  # The file of this pass is user_model.
        self.model_name = None
        self.model = None

        self.modification_list = [] # Modifications, defined in the defined by users previously.
        self.new_modifications = []
        self.author = None
        self.id_type = None

        self.edgeID_to_rxnID_table = {}
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

    def set_id_type(self, id_type: str):
        # if id_type does not specified, it treats the reaction IDs as it is.
        # (the IDs used in the base_model)
        self.id_type = id_type  
        print("id_type: {} registered.".format(id_type))

    def list_reaction_ids(self):
        self.model = cobra.io.read_sbml_model(self.base_model_path)
        return self.model.reactions.list_attr('id')

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
            "date" : date_str,
            "id_type" : self.id_type, 
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

    def _apply_modification(self, modification_commands, id_table = None):
        if self.model == None:
            raise 

        for command in modification_commands:
            if command[0] == "knockout":
                reaction_id = command[1]
                if id_table != None:
                    reaction_id = id_table[reaction_id]
                    print("# {} -> {}".format(command[1], reaction_id) )

                if self.model.reactions.has_id(reaction_id):
                    self.model.reactions.get_by_id(reaction_id).knock_out()
                else:
                    raise "Reaction {} is not found!".format(reaction_id)

            elif command[0] == "bound":
                reaction_id = command[1]
                if id_table != None:
                    reaction_id = id_table[reaction_id]
                    print("# {} -> {}".format(command[1]), reaction_id)
                lower_bound = float(command[2])
                upper_bound = float(command[3])
                if self.model.reactions.has_id(reaction_id):
                    self.model.reactions.get_by_id(reaction_id).bounds = (lower_bound, upper_bound)
                    print("apply: bound: {} {} {}".format(reaction_id, lower_bound, upper_bound))
                else:
                    raise "Reaction {} is not found!".format(reaction_id)
            else:
                raise "Unknown command"
                pass
        
    def do_FBA(self):
        # First, load the original model
        self.model = cobra.io.read_sbml_model(self.base_model_path)

        # second, apply the previously defined commands.
        for modification in self.modification_list:

            if "id_type" in modification and modification["id_type"] != None:
                # If id_type is specified, convert the reaction ids to the bigg_id.
                id_table = self.generate_edgeID_to_rxnID_map(modification["id_type"])
                self._apply_modification(modification["commands"], id_table)
            else:
                self._apply_modification(modification["commands"])

        
        # Third, apply the current commands
        if self.id_type != None:
            id_table = self.generate_edgeID_to_rxnID_map(self.id_type)
            self._apply_modification(self.new_modifications, id_table)
        else:
            self._apply_modification(self.new_modifications)

        with self.model:
            solution = self.model.optimize()

        data = {
            'fluxes': sorted(solution.fluxes.items(), key=lambda kv: kv[0]),
            'objective_value': solution.objective_value}

        return data

    def generate_edgeID_to_rxnID_map(self, view_path: str):
        """ convert reactions specified the edgeID to its original name """
        import json
        edgeID_to_rxnID ={}
        with open(view_path, 'r') as f:
            view = json.load(f)
            for edge in view["elements"]["edges"]:
                edge_id = edge["data"]["id"]
                rxn_id = edge["data"]["name"]
                edgeID_to_rxnID[edge_id] = rxn_id
        return edgeID_to_rxnID

    def get_reaction_information(self, reaction_db_file: str, reaction_id: str, view_path: str = None):
        print(reaction_db_file)
        column_names = []
        data = None

        if self.id_type != None:
            id_table = self.generate_edgeID_to_rxnID_map(self.id_type)
            if reaction_id in id_table:
                reaction_id = id_table[reaction_id]
            else:
                return {}

        find_flag = False
        with open(reaction_db_file) as f:
            for line_num, line in enumerate(f):
                record = line.lstrip().rstrip().split('\t')
                if line_num == 0:
                    column_names = record
                else:
                    if record[0] == reaction_id:
                        data = record
        ret = {}
        if data != None:
            for (k,v) in zip(column_names, data):
                ret[k] = v

        return ret



if __name__ == '__main__':
    mh = ModelHandler("iJO1366", "./models/iJO1366.xml")
    # Originally, this function should NOT be called by user.
    # This function should be called internally in load_user_model().(NOT called by users directory.)
    mh.add_modification_set({
        "author": "sakamoto", 
        "commands" : [
            ["bound", "DHPPD", 0.01, 0.5], 
            ["knockout", "DHAtex"]
            ]} 
            )
    print(mh.get_modification_set() )
    mh.add_modification_command(["knockout", "DHAtex"])
    print("hoger")
    mh.set_author("James")
    mh.set_model_name("testtest")
    mh.save_user_model("test222.yaml")
    
    mh2 = ModelHandler()
    mh2.load_user_model("test222.yaml")
    print(mh2.get_modification_set())
    #print(mh2.do_FBA())
    pass
