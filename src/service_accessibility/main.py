from fastapi import FastAPI
from .api import routes

def create_app():
    app = FastAPI()
    app.include_router(routes.router)
    return app

app = create_app()
