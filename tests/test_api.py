import requests

BASE_URL = "http://127.0.0.1:8000"


def test_browse_api():
    response = requests.get(f"{BASE_URL}/api/browse")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 5


def test_search_api():
    response = requests.get(f"{BASE_URL}/api/search")

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            "result-1",
            "result-2",
            "result-3",
        ]
    }


def test_checkout_api():
    response = requests.post(f"{BASE_URL}/api/checkout")

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"