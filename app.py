from fastapi import FastAPI, Query, Body, Response

import json
import cobra.io
from logging import getLogger
logger = getLogger(__name__)

MODELS = ['sample1']


app = FastAPI()

@app.get("/models")
def models():
    return {"models": MODELS}

@app.post("/sbml/{name}")
def model(name: str):
    if name not in MODELS:
        return {}

    with open(f'./models/{name}.xml', 'r') as f:
        data = f.read()
    return Response(content=data, media_type="application/xml")

@app.post("/model/{name}")
def model(name: str):
    if name not in MODELS:
        return {}

    with open(f'./models/{name}.cyjs', 'r') as f:
        data = json.load(f)
    return data

@app.post("/solve/{name}")
def solve(name: str, knockouts: str = Query(None)):
    if name not in MODELS:
        return {}

    if knockouts is None:
        knockouts = []
    else:
        knockouts = knockouts.split(',')
    print(knockouts)

    model = cobra.io.read_sbml_model(f'./models/{name}.xml')

    with model:
        for reaction_id in knockouts:
            if not model.reactions.has_id(reaction_id):
                #XXX: Say something here
                print(f'Reaction [{reaction_id}] not found.')
                continue

            model.reactions.get_by_id(reaction_id).knock_out()
        solution = model.optimize()

    data = solution.fluxes.copy()
    return data

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
