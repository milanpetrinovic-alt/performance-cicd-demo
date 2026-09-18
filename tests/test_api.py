import requests


def test_search_api():
    response = requests.get("http://127.0.0.1:8000/api/search")

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            "result-1",
            "result-2",
            "result-3",
        ]
    }