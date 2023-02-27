from fastapi.testclient import TestClient
from app import app
import urllib.parse

client=TestClient(app)

def test_list_models():
    response = client.get("/list_models/")
    assert response.status_code == 200
    assert "iJO1366" in response.json()["models"]
    assert "sample1" in response.json()["models"]

def test_list_views():
    response = client.get("/list_views/")
    assert response.status_code == 200
    assert "iJO1366" in response.json()["views"]
    assert "sample1" in response.json()["views"]

def test_get_model_property():
    response = client.get("/get_model_property/iJO1366")
    assert response.status_code == 200
    ret = response.json()
    assert ret["database_type"] == "bigg"
    assert ret["default_view"] == "iJO1366"
    assert ret["organ"] == "EColi"
    assert ret["version"] == "1.0.0"

def test_solve_normal():
    response = client.get("/solve/iJO1366/")
    assert response.status_code == 200

def test_solve_diff():
    query_normal = "/solve/sample1/"
    response_normal = client.get(urllib.parse.quote(query_normal))
    assert response_normal.status_code == 200
    print(response_normal.json())

    query_mod = "/solve/sample1/?commands=knockout#AtoB"
    print(urllib.parse.quote(query_mod))
    response_mod =    client.get(urllib.parse.quote(query_mod))
    assert response_mod.status_code == 200
    print(response_mod.json())

