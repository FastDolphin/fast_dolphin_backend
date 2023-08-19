from typing import Any

from fastapi import APIRouter, Response, status, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from typing import List
from pyhere import here
import sys

sys.path.append(str(here().resolve()))

from model import (
    CustomerRequest,
    CustomerRequestWithIdAndTimeStamp,
    RouterOutput,
)

from utils import WrongEmailFormat, AlreadyExistsError

import logging
from dotenv import dotenv_values

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")

router = APIRouter(prefix="/v1/new-requests", tags=["customer requests"])


@router.post("/", response_model=RouterOutput)
async def create_new_request(
    new_customer_request: CustomerRequest, response: Response, request: Request
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    all_existing_requests_of_this_customer = list(
        request.app.database.Requests.find({"Email": new_customer_request.Email})
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
    uploaded_customer_request = request.app.database.Requests.insert_one(
        encoded_new_customer_request
    )
    created_customer_request = request.app.database.Requests.find_one(
        {"_id": uploaded_customer_request.inserted_id}
    )

    output.Resources.append(
        CustomerRequestWithIdAndTimeStamp(**created_customer_request)
    )
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK

    # Publish the details of the newly created request to the RabbitMQ queue
    request.app.rabbitmq_channel.basic_publish(
        exchange="", routing_key="notify_admin", body=encoded_new_customer_request
    )

    return output


@router.get("/all", response_model=List[CustomerRequestWithIdAndTimeStamp])
async def read_all_requests(
    request: Request,
) -> List[CustomerRequestWithIdAndTimeStamp]:
    all_requests = request.app.database.Requests.find()
    return [CustomerRequestWithIdAndTimeStamp(**request) for request in all_requests]


@router.delete("/{id}", response_model=dict)
async def delete_request(id: str, request: Request):
    result = request.app.database.Requests.delete_one({"_id": id})
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
