from fastapi import APIRouter, Response, status, Request
from fastapi.encoders import jsonable_encoder
from typing import Optional
from pyhere import here  # type: ignore
import sys
import pika  # type: ignore

sys.path.append(str(here().resolve()))
from model import RouterOutput, Messages, MessagesWithId
import logging
from dotenv import dotenv_values

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
config = dotenv_values(".env")
router = APIRouter(prefix="/v1/messages", tags=["messages"])


@router.get("", response_model=RouterOutput)
async def get_messages(
    response: Response,
    request: Request,
    api_key: Optional[str] = None,
    tg_id: Optional[int] = None,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    messages_collection = request.app.database["messages_collection"]

    if api_key is None and tg_id is None:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        output.ErrorMessage = "Either `api_key` or `tg_id` must be provided"
        return output

    result = messages_collection.find_one({"TgId": tg_id})
    if not result:
        result = messages_collection.find_one({"ApiKey": api_key})
        if not result:
            response.status_code = status.HTTP_404_NOT_FOUND
            output.ErrorMessage = "Not found"
            return output

    messages: Messages = Messages(**result)
    output.Resources.append(messages.Messages)
    return output


@router.post("", response_model=RouterOutput)
async def create_messages(
    response: Response, messages: Messages, request: Request
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    messages_collection = request.app.database["messages_collection"]
    result = messages_collection.find_one({"TgIg": messages.TgId})
    if result:
        response.status_code = status.HTTP_409_CONFLICT
        output.ErrorMessage = "Already exists"
        return output
    else:
        result = messages_collection.find_one({"ApiKey": messages.ApiKey})
        if result:
            response.status_code = status.HTTP_409_CONFLICT
            output.ErrorMessage = "Already exists"
            return output

    messages_with_id = MessagesWithId(**messages.dict())
    encoded_messages = jsonable_encoder(messages_with_id)
    uploaded_messages = messages_collection.insert_one(encoded_messages)
    created_messages = messages_collection.find_one(
        {"_id": uploaded_messages.inserted_id}
    )
    output.Resources.append(created_messages)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.get("/all", response_model=RouterOutput)
async def get_all_messages(request: Request, response: Response) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    messages_collection = request.app.database["messages_collection"]
    results = list(messages_collection.find(limit=100))
    if results:
        output.Resources = [Messages(**result) for result in results]

    response.status_code = status.HTTP_200_OK
    output.StatusMessage = "Success"
    return output
