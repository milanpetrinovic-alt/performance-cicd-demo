import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/api/search")
def search():
    time.sleep(0.7)

    return {
        "results": [
            "result-1",
            "result-2",
            "result-3",
        ]
    }