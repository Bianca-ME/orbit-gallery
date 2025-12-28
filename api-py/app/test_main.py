from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_create_photo():
    response = client.post(
        "/photos/",
        json={
            "title": "Test photo",
            "tags": ["nature", "sky"],
            "s3_key": "test_image.jpg"
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["title"] == "Test photo"
    assert "id" in data

def test_read_photos():
    response = client.get("/photos/")
    assert response.status_code == 200, response.text
    assert isinstance(response.json(), list)
