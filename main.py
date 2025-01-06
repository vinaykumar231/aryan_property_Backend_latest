from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from api.endpoints import (user_rouetr)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = FastAPI.openapi(app)  
    openapi_schema["info"]["title"] = "Aryans Properties"
    openapi_schema["info"]["version"] = "1.1.0"
    openapi_schema["info"]["description"] = "This API serves as the backend for Aryans Properties."
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_rouetr, prefix="/api", tags=["user Routes"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8003, reload= True, host="0.0.0.0")