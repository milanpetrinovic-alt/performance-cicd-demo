from fastapi import FastAPI

app = FastAPI()


@app.get("/api/search")
def search():
    return {
        "results": [
            "result-1",
            "result-2",
            "result-3",
        ]
    }