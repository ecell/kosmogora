import os

def get_reaction_information_bigg(reaction_id):
    dbfilename = './models/bigg_models_reactions.txt'
    column_names = None
    data = None
    with open(dbfilename) as f:
        for line_num, line in enumerate(f):
            record = line.lstrip().rstrip().split('\t')
            if line_num == 0:
                column_names = record
            else:
                if record[0] == reaction_id:
                    data = record
                    break
    ret = {}
    if data != None:
        for (k,v) in zip(column_names, data):
            ret[k] = v
    return ret

def get_reaction_information_mtnx(reaction_id):
    dbfilename = "reac_prop.tsv"
    ret = None
    '''
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
                            "MNX_ID": record[0],
                            "EQUATION": record[1],
                            "REFERENCE": record[2],
                            "ECs": record[3],
                            "IS_BALANCED": record[4],
                            "IS_TRNSPORT": record[5]
                    }
                    break
    return ret

def convert_name(src_db, src_id, dst_db):
    db_file = 'id2id.tsv'
    ret = None
    with open(db_file) as f:
        for line in f:
            record = line.rstrip().split('\t')
            if record[0] == src_db and record[1] == src_id and record[2] == dst_db:
                ret = record[3]
                break
    return ret

if __name__ == '__main__':
    name_mtx = convert_name("bigg.reaction", "EX_galside_cho_e", "metanetx.reaction") 
    print("{} ===>>> {}".format("EX_galside_cho_e", name_mtx))
    print("==== From Bigg ====")
    print(get_reaction_information_bigg("EX_galside_cho_e"))
    print("==== From MetaNetX ====")
    print(get_reaction_information_mtnx(name_mtx))
