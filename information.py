import os
import sys

def get_reaction_information_bigg(reaction_id):
    dbfilename = './models/bigg_models_reactions.txt'
    column_names = None
    data = None
    ret = {}
    with open(dbfilename) as f:
        for line_num, line in enumerate(f):
            record = line.lstrip().rstrip().split('\t')
            if line_num == 0:
                column_names = record
            else:
                if record[0] == reaction_id:
                    data = record
                    ret = {
                            "ID": record[0],
                            "NAME": record[1],
                            "REACTION": record[2],
                            "MODEL_LIST": record[3],
                            "DATABASE_STRING": record[4],
                            "OLD_BIGG_IDs": record[5]
                    }
                    break
    return ret

def get_reaction_information_mtnx(reaction_id):
    dbfilename = "./models/reac_prop.tsv"
    ret = None
    '''
    Columns separated by TAB are as follows.

    The identifier of the reaction in the MNXref namespace [MNX_ID]
    Equation of the reaction in the MNXref namespace (compartmentalized and undirected) [EQUA]
    The original best resource from where this reaction comes from [REFERENCE]
    The EC(s) associated to this reaction [STRING]
    Is the equation balanced with respect to elemental composition and charge [BOOLEAN]
    Is this a transport reaction [BOOLEAN]
    '''
    with open(dbfilename) as f:
        for line in f:
            if line[0] == '#':
                continue
            record = line.rstrip().split('\t')
            if len(record) == 6:
                if record[0] == reaction_id:
                    # pack
                    ret = {
                            "ID": record[0],
                            "EQUATION": record[1],
                            "REFERENCE": record[2],
                            "ECs": record[3],
                            "IS_BALANCED": record[4],
                            "IS_TRNSPORT": record[5]
                    }
                    break
    return ret

def get_reaction_information(reaction_id, db_src):
    if db_src == "metanetx" or db_src == "metanetx.reaction":
        return get_reaction_information_mtnx(reaction_id)
    elif db_src == "bigg" or db_src == "bigg.reaction":
        return get_reaction_information_bigg(reaction_id)
    else:
        return None

def convert_name(src_db, src_id, dst_db):
    db_file = './models/id2id.tsv'
    ret = None
    with open(db_file) as f:
        for line in f:
            record = line.rstrip().split('\t')
            if record[0] == src_db and record[1] == src_id and record[2] == dst_db:
                ret = record[3]
                break
    return ret

def available_reaction_db():
    return {"bigg", "metanetx"}

if __name__ == '__main__':
    name_mtx = convert_name("bigg.reaction", "EX_galside_cho_e", "metanetx.reaction") 
    if name_mtx == None:
        sys.exit()
    print(available_reaction_db())
    print("{} ===>>> {}".format("EX_galside_cho_e", name_mtx))
    print("==== From Bigg ====")
    print(get_reaction_information_bigg("EX_galside_cho_e"))
    print("==== From MetaNetX ====")
    print(get_reaction_information_mtnx(name_mtx))
