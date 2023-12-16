import os
import asyncio
from fastapi import FastAPI, Depends
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routers import (
    new_requests,
    training_plans,
    user_with_achievements,
    parent_training,
    personal_training,
    authorization,
    allowed,
)
from pyhere import here  # type: ignore
import sys

sys.path.append(str(here().resolve()))

from utils import CorsConstants, connect_to_rabbitmq
from .auth import get_client_api_key, get_admin_api_key

load_dotenv()

__STAGE__ = os.getenv("__STAGE__", "prod")
MONGO_INITDB_ROOT_USERNAME = os.environ["MONGO_INITDB_ROOT_USERNAME"]
MONGO_INITDB_ROOT_PASSWORD = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
DB_NAME = os.environ["MONGODB_NAME"]
REQUESTS_COLLECTION = os.environ["REQUESTS_COLLECTION"]
TRAINING_PLANS_COLLECTION = os.environ["TRAININGPLANS_COLLECTION"]
USER_WITH_ACHIEVEMENTS_COLLECTION = os.environ["USERWITHACHIEVEMENTS_COLLECTION"]
PERSONAL_TRAINING_COLLECTION = os.environ["PERSONALTRAINING_COLLECTION"]
PERSONAL_TRAINING_METADATA_COLLECTION = os.environ[
    "PERSONALTRAININGMETADATA_COLLECTION"
]
PERSONAL_TRAINING_REPORT_COLLECTION = os.environ["PERSONALTRAININGREPORT_COLLECTION"]
MONGO_DETAILS = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017/{DB_NAME}?authSource=admin"
if __STAGE__ == "dev":
    MONGO_DETAILS = "mongodb://localhost:27017"
RABBITMQ_DEFAULT_USER = os.environ["RABBITMQ_DEFAULT_USER"]
RABBITMQ_DEFAULT_PASS = os.environ["RABBITMQ_DEFAULT_PASS"]
RABBITMQ_HOST = os.environ["RABBITMQ_HOST"]

app = FastAPI()


@app.on_event("startup")
def startup_event():
    # MongoDB client initialization
    app.mongodb_client = MongoClient(MONGO_DETAILS)
    app.database = app.mongodb_client[DB_NAME]
    app.requests_collection = app.database[REQUESTS_COLLECTION]
    app.trainingplans_collection = app.database[TRAINING_PLANS_COLLECTION]
    app.userwithachievements_collection = app.database[
        USER_WITH_ACHIEVEMENTS_COLLECTION
    ]
    app.personaltraining_collection = app.database[PERSONAL_TRAINING_COLLECTION]
    app.personaltrainingmetadata_collection = app.database[
        PERSONAL_TRAINING_METADATA_COLLECTION
    ]
    app.personaltrainingreport_collection = app.database[
        PERSONAL_TRAINING_REPORT_COLLECTION
    ]
    if __STAGE__ != "dev":
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
    if __STAGE__ != "dev":
        app.rabbitmq_connection.close()


app.include_router(new_requests.router)
app.include_router(training_plans.router)
app.include_router(user_with_achievements.router)
app.include_router(parent_training.router)
app.include_router(allowed.router)
app.include_router(personal_training.router, dependencies=[Depends(get_client_api_key)])
app.include_router(authorization.router, dependencies=[Depends(get_admin_api_key)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CorsConstants.DEV_ORIGINS,
    allow_headers=CorsConstants.DEV_HEADERS,
    allow_methods=CorsConstants.METHODS,
    allow_credentials=True,
)
