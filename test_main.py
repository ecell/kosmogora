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

def test_call_view():
    response = client.get('/view/iJO1366')
    assert  response.status_code == 200
    

