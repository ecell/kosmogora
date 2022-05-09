from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


# First, list the registered model.
def test_call_models():
    response = client.get("/models")
    assert response.status_code == 200
    assert response.json() == {"models": ["sample1", "iJO1366"]}

# Second, List the views related to iJO1366
def test_call_views():
    response = client.get("/views/iJO1366")
    assert response.status_code == 200
    assert response.json() == {"views": ["iJO1366"]}
    
# Third, get the model in *.xml of iJO1366
def test_call_sbml():
    response = client.get('/sbml/iJO1366')
    assert response.status_code == 200

# Get the model in *.xml of iJO1366. This is same as sbml() at present.
def test_call_model():
    response = client.get('/model/iJO1366')
    assert response.status_code == 200

# Get the view in *.cyjs format of iJO1366 (<- view name, not model name)
def test_call_view():
    response = client.get('/view/iJO1366')
    assert response.status_code == 200

# Execute the FBA.
def test_call_solve():
    response = client.get('/solve/iJO1366')
    assert "fluxes" in response.json()
    assert "objective_value" in response.json()
    assert abs(response.json()["objective_value"] - 0.9823718127269787) < 0.0001
    assert response.status_code == 200

    #Try knowkout
    response2 = client.get('/solve/iJO1366?knockouts=UPP3S,EX_so4_e')
    assert "fluxes" in response2.json()
    assert "objective_value" in response2.json()
    assert response.status_code == 200