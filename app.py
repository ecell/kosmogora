from fastapi import FastAPI, Query, Body, Response

import json
import cobra.io
from logging import getLogger
logger = getLogger(__name__)

MODELS = ['sample1']

class XMLResponse(Response):
    media_type = "application/xml"


app = FastAPI()

@app.get("/models")
def models():
    return {"models": MODELS}

@app.get("/sbml/{name}", response_class=XMLResponse)
def sbml(name: str):
    if name not in MODELS:
        return Response(content='<?xml version="1.0" encoding="UTF-8"?>', media_type="application/xml")

    with open(f'./models/{name}.xml', 'r') as f:
        data = f.read()
    return Response(content=data, media_type="application/xml")

@app.get("/model/{name}")
def model(name: str):
    if name not in MODELS:
        return {}

    with open(f'./models/{name}.cyjs', 'r') as f:
        data = json.load(f)
    return data

@app.get("/solve/{name}")
def solve(name: str, knockouts: str = Query(None)):
    if name not in MODELS:
        return {}

    if knockouts is None:
        knockouts = []
    else:
        knockouts = knockouts.split(',')

    model = cobra.io.read_sbml_model(f'./models/{name}.xml')

    with model:
        for reaction_id in knockouts:
            if not model.reactions.has_id(reaction_id):
                #XXX: Say something here
                logger.warn(f'Reaction [{reaction_id}] not found.')
                continue

            model.reactions.get_by_id(reaction_id).knock_out()
        solution = model.optimize()

    data = {
        'fluxes': sorted(solution.fluxes.items(), key=lambda kv: kv[0]),
        'objective_value': solution.objective_value}
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
