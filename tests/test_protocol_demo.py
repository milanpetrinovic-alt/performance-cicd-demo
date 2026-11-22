"""Protocol-demo API smoke check (expects uvicorn running, like existing tests)."""
import os

import requests

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def test_protocol_demo_search_returns_product_data():
    response = requests.get(f"{BASE_URL}/protocol-demo/api/search", params={"q": "laptop"}, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "laptop"
    assert data["total"] == len(data["results"]) == 3
    assert all("Laptop" in item["name"] for item in data["results"])


def test_protocol_demo_page_is_served():
    response = requests.get(f"{BASE_URL}/protocol-demo", timeout=5)
    assert response.status_code == 200
    assert "search-form" in response.text
