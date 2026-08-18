from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/{path:path}")
def test_app(path: str = ""):
    return PlainTextResponse("Minimal Test App Working!")
