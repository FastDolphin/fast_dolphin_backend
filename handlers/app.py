import time

from fastapi import FastAPI, Depends
from pymongo import MongoClient
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from .routers import new_requests

from pyhere import here
import sys
import pika

sys.path.append(str(here().resolve()))

from utils import CorsConstants

config = dotenv_values(".env")


app = FastAPI()


@app.on_event("startup")
def startup_event():
    # MongoDB client initialization
    MONGO_INITDB_ROOT_USERNAME = config["MONGO_INITDB_ROOT_USERNAME"]
    MONGO_INITDB_ROOT_PASSWORD = config["MONGO_INITDB_ROOT_PASSWORD"]
    DB_NAME = config["MONGODB_NAME"]

    MONGO_DETAILS = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017/{DB_NAME}?authSource=admin"
    app.mongodb_client = MongoClient(MONGO_DETAILS)
    app.database = app.mongodb_client[DB_NAME]

    # RabbitMQ connection initialization
    RABBITMQ_DEFAULT_USER = config["RABBITMQ_DEFAULT_USER"]
    RABBITMQ_DEFAULT_PASS = config["RABBITMQ_DEFAULT_PASS"]
    RABBITMQ_HOST = config["RABBITMQ_HOST"]

    max_retries = 10
    retry_delay = 5  # in seconds

    for _ in range(max_retries):
        try:
            print(f"Attempting to connect to RabbitMQ host: {RABBITMQ_HOST}")
            credentials = pika.PlainCredentials(
                RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS
            )
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST, credentials=credentials
            )
            app.rabbitmq_connection = pika.BlockingConnection(parameters)
            app.rabbitmq_channel = app.rabbitmq_connection.channel()
            app.rabbitmq_channel.queue_declare(queue="notify_admin")
            print("Connected to RabbitMQ successfully!")
            break
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            time.sleep(retry_delay)
    else:
        raise Exception("Failed to connect to RabbitMQ after multiple retries")


@app.on_event("shutdown")
def shutdown_event():
    app.mongodb_client.close()
    app.rabbitmq_connection.close()


app.include_router(new_requests.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CorsConstants.DEV_ORIGINS,
    allow_headers=CorsConstants.DEV_HEADERS,
    allow_methods=CorsConstants.METHODS,
    allow_credentials=True,
)
