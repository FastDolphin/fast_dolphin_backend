import logging
from typing import List, Dict, Any
from dotenv import dotenv_values
from fastapi import APIRouter, Request, Response, status
from datetime import datetime
from model import APIKey, APIKeyResponse, RouterOutput
from ..auth import is_admin_user

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")

router = APIRouter(prefix="/v1/allowed_api_key", tags=["allowed"])


@router.get("", response_model=RouterOutput)
async def is_api_key_allowed(
    request: Request, api_key: str, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    response.status_code = status.HTTP_403_FORBIDDEN
    output.ErrorMessage = "Access denied"
    if is_admin_user(api_key):
        response.status_code = status.HTTP_200_OK
        output.StatusMessage = "Success"
        output.Resources.append(APIKeyResponse(Allowed=True, ExpiresAt="never"))
        output.ErrorMessage = ""
        return output

    authorization_collection = request.app.database["authorization_collection"]
    all_existing_keys_of_this_user: List[Dict[str, Any]] = list(
        authorization_collection.find({"ApiKey": api_key})
    )
    if all_existing_keys_of_this_user:
        found_keys: List[APIKey] = [
            APIKey(**found_key) for found_key in all_existing_keys_of_this_user
        ]
        for key in found_keys:
            if key.ApiKey == api_key and key.ExpiresAt > datetime.now().isoformat():
                api_key_response: APIKeyResponse = APIKeyResponse(
                    Allowed=True, ExpiresAt=key.ExpiresAt
                )
                response.status_code = status.HTTP_200_OK
                output.StatusMessage = "Success"
                output.Resources.append(api_key_response)
                output.ErrorMessage = ""
    return output
