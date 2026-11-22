from fastapi import FastAPI
from app.protocol_demo import router as protocol_demo_router

app = FastAPI()
app.include_router(protocol_demo_router)


@app.get("/api/search")
def search():
    return {
        "results": [
            "result-1",
            "result-2",
            "result-3",
        ]
    }