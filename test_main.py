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

def test_call_model_property():
    response = client.get('/model_property/iJO1366')
    assert response.status_code == 200
    assert response.json() == {"database_type" : "bigg", "default_view" : "iJO1366", "version" : "1.0.0", "organ" : "EColi" }

# Get the view in *.cyjs format of iJO1366 (<- view name, not model name)
def test_call_view():
    response = client.get('/view/iJO1366')
    assert response.status_code == 200

def test_call_view_property():
    response = client.get('/view_property/sample1')
    assert response.status_code == 200
    assert response.json() == {"database_type" : "kegg", "model" : "sample1", "version" : "1.0.0", "organ" : "EColi" }

def test_edit_model():
    response = client.get('edit/iJO1366/bound_DHPPD_0.01_0.5,bound_DHPPD_-0.01_0.2,knockout_DHAtex')
    assert response.status_code == 200
    assert response.json()[0] == True

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