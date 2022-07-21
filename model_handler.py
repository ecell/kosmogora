import json
import cobra.io 
from typing import Optional

class ModelHandler:
    '''
    This class manages to do the FBA and modify the models.
    '''
    def __init__(self, base_filename : Optional[str] = None, view_path : Optional[str] = None ):
        self.base_filename = base_filename
        self.applied_commands = []
        self.num_modified = 0   # the number of the applied modification
        self.model = None

        self.view_path = view_path
        self.rxn_specified_by_viewid = False

        if base_filename != None:
            self.load_model(base_filename)

        if view_path != None:
            self.set_view_file(view_path)

    def load_model(self, base_filename: str) -> None:
        self.base_filename = base_filename
        self.model = cobra.io.read_sbml_model(base_filename)

    def set_view_file(self, view_path: str) -> None:
        # Generate table that relate the edge_id to reaction_id defined in database.
        self.view_path = view_path
        self.edgeID_to_rxnID = {}
        with open(self.view_path, 'r') as f:
            view = json.load(f)
            for edge in view["elements"]["edges"]:
                edge_id = edge["data"]["id"]
                rxn_id = edge["data"]["bigg_id"]
                self.edgeID_to_rxnID[edge_id] = rxn_id
        self.rxn_specified_by_viewid = True

    def load_user_model(self, usermodel_path: str) -> None :
        '''
        Load and apply the modification defined by users, which is based on the pre-defined model.
        '''
        import yaml 
        user_defined_data = dict()
        with open(usermodel_path) as file:
            user_defined_data = yaml.safe_load(file)

        assert "base_model_path" in user_defined_data
        assert "modification" in user_defined_data
        if "view_path" in user_defined_data:
            self.set_view_file(user_defined_data["view_path"])
        self.load_model(user_defined_data["base_model_path"])
        self.edit_model_by_query_str(user_defined_data["modification"])
    
    def save_user_model(self, outfile_path: str, author : str, description : str) -> None :
        '''
        Save the modifications defined by the users.
        '''
        import yaml
        data = {
            "base_model_path" : self.base_filename,
            "modification" : ','.join(self.applied_commands) ,
            "author" : author,
            "description" : description
        }   
        if self.rxn_specified_by_viewid == True:
            data["view_path"] = self.view_path
        with open(outfile_path, "w") as file:
            yaml.dump(data, file)


    def apply_bounds(self, reaction_id : str, lower_bound: float, upper_bound : float) -> bool:
        '''
        Edit the boundary of the specified reaction.
        This function is called by the edit_model_by_query_str() internally.
        '''
        assert self.model != None
        ret_flag = False
        if self.model.reactions.has_id(reaction_id):
            self.model.reactions.get_by_id(reaction_id).bounds = (lower_bound, upper_bound)
            self.num_modified += 1
            ret_flag = True 
        return ret_flag
            
    def apply_knockout(self, reaction_id: str) -> bool :
        '''
        Knockout specified reaction.
        This function is called by the edit_model_by_query_str() internally.
        '''
        assert self.model != None
        ret_flag = False
        if self.model.reactions.has_id(reaction_id):
            self.model.reactions.get_by_id(reaction_id).knock_out()
            self.num_modified += 1
            ret_flag = True 
        return ret_flag

    def edit_model_by_query_str(self, commands: str = None) -> int:
        '''
        Process and apply the commands.
        '''
        if commands == None:
            commands = []
        else:
            commands = commands.split(',')
            
        print(commands)
        for cmd in commands:
            cmd = cmd.split('#')
            print(cmd)
            if cmd[0] == "bound":
                assert len(cmd) == 4
                reaction_id = cmd[1]
                if self.rxn_specified_by_viewid == True:
                    reaction_id = self.edgeID_to_rxnID[cmd[1]]
                    print(f"boundary: rxn-id conversion: {cmd[1]} => {reaction_id}")           

                lower_bound, upper_bound = float(cmd[2]), float(cmd[3])
                result = self.apply_bounds(reaction_id, lower_bound, upper_bound)
                if result != True:
                    raise Exception("apply bound failure")

            elif cmd[0] == "knockout":
                assert len(cmd) == 2
                reaction_id = cmd[1]

                if self.rxn_specified_by_viewid == True:
                    reaction_id = self.edgeID_to_rxnID[cmd[1]]
                    print(f"knockout: rxn-id conversion: {cmd[1]} => {reaction_id}")           

                result = self.apply_knockout(reaction_id)
                if result != True:
                    raise Exception("apply knockout failure")
        self.applied_commands += commands    

        return self.num_applied_modification()

    def solve(self):
        """
        Execute the flux balance analysis.
        """
        assert self.model != None
        with self.model:
            solution = self.model.optimize()

        data = {
            'fluxes': sorted(solution.fluxes.items(), key=lambda kv: kv[0]),
            'objective_value': solution.objective_value}

        return data

    def num_applied_modification(self) -> int:
        '''
        returns the number of the applied modifications.
        '''
        return self.num_modified
