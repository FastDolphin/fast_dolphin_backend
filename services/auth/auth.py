from fastapi import Request, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typeguard import typechecked
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")
api_key_header = APIKeyHeader(name="X-API-Key")


@typechecked
def is_client_user_v2(request: Request, api_key: str) -> bool:
    authorization_collection = request.app.database["authorization_collection"]
    current_time = datetime.now().isoformat()
    key = authorization_collection.find_one(
        {"ApiKey": api_key, "ExpiresAt": {"$gt": current_time}}
    )
    return key is not None


@typechecked
def get_client_api_key(
    request: Request, api_key_header: str = Security(api_key_header)
) -> str:
    if is_client_user_v2(request, api_key_header) or is_admin_user(api_key_header):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


@typechecked
def is_admin_user(token: str) -> bool:
    return token == config["ADMIN_TOKEN"]


@typechecked
def get_admin_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if is_admin_user(api_key_header):
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
