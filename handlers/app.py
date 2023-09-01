import asyncio

from fastapi import FastAPI, Depends
from pymongo import MongoClient
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from .routers import new_requests, training_plans

from pyhere import here
import sys

sys.path.append(str(here().resolve()))

from utils import CorsConstants, connect_to_rabbitmq

config = dotenv_values(".env")
MONGO_INITDB_ROOT_USERNAME = config["MONGO_INITDB_ROOT_USERNAME"]
MONGO_INITDB_ROOT_PASSWORD = config["MONGO_INITDB_ROOT_PASSWORD"]
DB_NAME = config["MONGODB_NAME"]
REQUESTS_COLLECTION = config["REQUESTS_COLLECTION"]
TRAININGPLANS_COLLECTION = config["TRAININGPLANS_COLLECTION"]
MONGO_DETAILS = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017/{DB_NAME}?authSource=admin"

RABBITMQ_DEFAULT_USER = config["RABBITMQ_DEFAULT_USER"]
RABBITMQ_DEFAULT_PASS = config["RABBITMQ_DEFAULT_PASS"]
RABBITMQ_HOST = config["RABBITMQ_HOST"]

app = FastAPI()


@app.on_event("startup")
def startup_event():
    # MongoDB client initialization
    app.mongodb_client = MongoClient(MONGO_DETAILS)
    app.database = app.mongodb_client[DB_NAME]
    app.requests_collection = app.database[REQUESTS_COLLECTION]
    app.trainingplans_collection = app.database[TRAININGPLANS_COLLECTION]
    app.metadata_collection = app.database[METADATA_COLLECTION]
    app.rabbitmq_connection, app.rabbitmq_channel = connect_to_rabbitmq(
        RABBITMQ_HOST, RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS
    )
    asyncio.create_task(monitor_rabbitmq_connection())


# Proactive Monitoring (optional but recommended)
async def monitor_rabbitmq_connection():
    while True:
        if not app.rabbitmq_connection.is_open:
            print("RabbitMQ connection lost. Reconnecting...")
            app.rabbitmq_connection, app.rabbitmq_channel = connect_to_rabbitmq(
                RABBITMQ_HOST, RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS
            )
        await asyncio.sleep(60)  # check every minute


@app.on_event("shutdown")
def shutdown_event():
    app.mongodb_client.close()
    app.rabbitmq_connection.close()


app.include_router(new_requests.router)
app.include_router(training_plans.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CorsConstants.DEV_ORIGINS,
    allow_headers=CorsConstants.DEV_HEADERS,
    allow_methods=CorsConstants.METHODS,
    allow_credentials=True,
)
