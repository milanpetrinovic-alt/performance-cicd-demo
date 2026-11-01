from fastapi import FastAPI

app = FastAPI()


@app.get("/api/browse")
def browse():
    return {
        "items": [
            "item-1",
            "item-2",
            "item-3",
            "item-4",
            "item-5",
        ]
    }


@app.get("/api/search")
def search():
    return {
        "results": [
            "result-1",
            "result-2",
            "result-3",
        ]
    }


@app.post("/api/checkout")
def checkout():
    return {
        "order_id": "demo-order-001",
        "status": "confirmed",
    }