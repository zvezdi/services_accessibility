from fastapi.testclient import TestClient
from service_accessibility.main import create_app

def test_get_schools():
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/schools")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    if len(data["features"]) > 0:
        feature = data["features"][0]
        assert "type" in feature
        assert "geometry" in feature
        assert "properties" in feature
        assert "gid" in feature["properties"]
        assert "subgroup" in feature["properties"]