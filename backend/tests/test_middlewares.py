from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middlewares import ExceptionMiddleware
from app.exceptions import AppError

def test_middleware_handles_app_error():
    app = FastAPI()
    app.add_middleware(ExceptionMiddleware)

    @app.get("/fail")
    def fail():
        raise AppError("custom error")

    client = TestClient(app)
    res = client.get("/fail")
    assert res.status_code == 400
    assert res.json()["type"] == "AppError"

def test_middleware_handles_unknown_error():
    app = FastAPI()
    app.add_middleware(ExceptionMiddleware)

    @app.get("/fail2")
    def fail2():
        raise RuntimeError("boom")

    client = TestClient(app)
    res = client.get("/fail2")
    assert res.status_code == 500
    assert res.json()["type"] == "UnhandledException"
