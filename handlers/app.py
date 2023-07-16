from fastapi import FastAPI, Depends
from pymongo import MongoClient
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from .routers import new_requests

from pyhere import here
import sys

sys.path.append(str(here().resolve()))

from utils import CorsConstants

config = dotenv_values(".env")


app = FastAPI()


@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["MONGO_ADDRESS"])
    app.database = app.mongodb_client[config["DB_NAME"]]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(new_requests.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CorsConstants.DEV_ORIGINS,
    allow_headers=CorsConstants.DEV_HEADERS,
    allow_methods=CorsConstants.METHODS,
    allow_credentials=True,
)
