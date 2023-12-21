import logging
from typing import Dict, Any

from bson import ObjectId
from dotenv import dotenv_values
from fastapi import APIRouter, Request, Response, status, HTTPException
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from model import APIKeyWithId, APIKey, RouterOutput, APIKeyMetadata
from uuid import uuid4

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")
router = APIRouter(prefix="/v1/authorization", tags=["authorization"])


@router.post(
    "/create_api_key",
    response_model=RouterOutput,
)
async def create_api_key(
    request: Request, response: Response, metadata: APIKeyMetadata
) -> RouterOutput:
    output = RouterOutput(ErrorMessage="Failed to create API key")
    new_api_key: APIKey = APIKey(
        ApiKey=str(uuid4()),
        GeneratedAt=datetime.now().isoformat(),
        ExpiresAt=(datetime.now() + timedelta(days=metadata.Days)).isoformat(),
        Metadata=metadata,
    )
    authorization_collection = request.app.database["authorization_collection"]
    encoded_new_api_key = jsonable_encoder(new_api_key)
    uploaded_api_key = authorization_collection.insert_one(encoded_new_api_key)
    created_api_key: Dict[str, Any] = authorization_collection.find_one(
        {"_id": uploaded_api_key.inserted_id}
    )
    api_key: APIKey = APIKey(**created_api_key)
    if api_key.ApiKey == new_api_key.ApiKey:
        output.StatusMessage = "Success"
        response.status_code = status.HTTP_200_OK
        created_api_key["_id"] = str(created_api_key["_id"])
        output.Resources.append(APIKeyWithId(**created_api_key))
        output.ErrorMessage = ""
    return output


@router.delete(
    "/delete_api_key/{api_key_id}",
    response_model=dict,
)
async def delete_api_key(api_key_id: str, request: Request) -> Dict[str, str]:
    authorization_collection = request.app.database["authorization_collection"]
    api_key_id_obj: ObjectId = ObjectId(api_key_id)
    result = authorization_collection.delete_one({"_id": api_key_id_obj})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")

    return {"detail": "API key deleted successfully"}


@router.get(
    "/get_api_keys",
    response_model=RouterOutput,
)
async def get_api_keys(
    request: Request,
    response: Response,
) -> RouterOutput:
    output = RouterOutput(ErrorMessage="No API keys found.")
    response.status_code = status.HTTP_404_NOT_FOUND

    authorization_collection = request.app.database["authorization_collection"]
    api_keys = authorization_collection.find(limit=100)
    if api_keys:
        for key in api_keys:
            key["_id"] = str(key["_id"])
            output.Resources.append(APIKeyWithId(**key))
            response.status_code = status.HTTP_200_OK
            output.ErrorMessage = ""
            output.StatusMessage = "Success"
    return output
