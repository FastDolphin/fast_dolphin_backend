from fastapi import APIRouter, Response, status, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import List
from pyhere import here
import sys
import json
import pika
import logging
from model import (
    CustomerRequest,
    CustomerRequestWithIdAndTimeStamp,
    RouterOutput,
)
from utils import WrongEmailFormat, AlreadyExistsError
from dotenv import dotenv_values

sys.path.append(str(here().resolve()))
config = dotenv_values(".env")
ROUTING_KEY: str = config.get("ROUTING_KEY")

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/v1/new-requests", tags=["customer requests"])


@router.post("/", response_model=RouterOutput)
async def create_new_request(
    new_customer_request: CustomerRequest, response: Response, request: Request
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    all_existing_requests_of_this_customer = list(
        request.app.requests_collection.find({"Email": new_customer_request.Email})
    )

    if all_existing_requests_of_this_customer:
        existing_request_no_timestamp = [
            CustomerRequest(**existing_request).dict()
            for existing_request in all_existing_requests_of_this_customer
        ]
        if is_new_request_equal_to_any_existing(
            new_customer_request.dict(), existing_request_no_timestamp
        ):
            raise AlreadyExistsError()

    new_customer_request_with_timestamp = CustomerRequestWithIdAndTimeStamp(
        **new_customer_request.dict()
    )

    if not new_customer_request_with_timestamp.has_valid_email():
        raise WrongEmailFormat()

    encoded_new_customer_request = jsonable_encoder(new_customer_request_with_timestamp)
    uploaded_customer_request = request.app.requests_collection.insert_one(
        encoded_new_customer_request
    )
    created_customer_request = request.app.requests_collection.find_one(
        {"_id": uploaded_customer_request.inserted_id}
    )

    output.Resources.append(
        CustomerRequestWithIdAndTimeStamp(**created_customer_request)
    )
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK

    encoded_new_customer_request_string: str = json.dumps(encoded_new_customer_request)
    MAX_RETRIES: int = 5
    for attempt in range(MAX_RETRIES):
        try:
            # Check if the connection and channel are open
            if (
                not request.app.rabbitmq_connection.is_open
                or not request.app.rabbitmq_channel.is_open
            ):
                # Log the state
                logging.warning(
                    "RabbitMQ connection or channel is closed. Attempting to reconnect..."
                )

                # Re-establish the connection and channel
                request.app.rabbitmq_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host="rabbitmq")
                )
                request.app.rabbitmq_channel = request.app.rabbitmq_connection.channel()

            # Try publishing the message
            request.app.rabbitmq_channel.basic_publish(
                exchange="",
                routing_key=ROUTING_KEY,
                body=encoded_new_customer_request_string,
            )
            break  # If successful, exit the loop
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}: Error publishing to RabbitMQ: {e}")
            if attempt == MAX_RETRIES - 1:
                # After all retries, if still unsuccessful
                # Additional error handling can be done here, like raising a custom exception
                raise Exception(
                    f"Failed to publish to RabbitMQ after {MAX_RETRIES} attempts."
                )

    return output


@router.get("/all", response_model=List[CustomerRequestWithIdAndTimeStamp])
async def read_all_requests(
    request: Request,
) -> List[CustomerRequestWithIdAndTimeStamp]:
    all_requests = request.app.requests_collection.find()
    return [CustomerRequestWithIdAndTimeStamp(**request) for request in all_requests]


@router.delete("/{id}", response_model=dict)
async def delete_request(id: str, request: Request):
    result = request.app.requests_collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"detail": "Document deleted successfully"}


def is_new_request_equal_to_any_existing(
    new_request: dict, existing_requests: list[dict]
) -> bool:
    return any(
        sorted(existing.items()) == sorted(new_request.items())
        for existing in existing_requests
    )
