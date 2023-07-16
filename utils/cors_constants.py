from dataclasses import dataclass
from typing import Final, Tuple


@dataclass
class CorsConstants:
    DEV_ORIGINS: Final[Tuple[str]] = (
        "http://127.0.0.1:5050",
        "capacitor://localhost",
        "http://localhost",
        "ionic://localhost",
        "http://localhost:5050",
        "http://127.0.0.1:5050/login",
        "http://localhost:5050/login",
    )
    DEV_HEADERS: Final[Tuple[str]] = (
        "Content-Type",
        "X-Amz-Date",
        "X-Amz-Security-Token",
        "Authorization",
        "X-Api-Key",
        "X-Requested-With",
        "Accept",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Headers",
    )
    METHODS: Final[Tuple[str]] = (
        "GET",
        "OPTIONS",
        "POST",
        "PUT",
        "DELETE",
        "HEAD",
        "PATCH",
    )

    FULL_HEADERS = {
        "Access-Control-Allow-Headers": ",".join(DEV_HEADERS),
        "Access-Control-Allow-Origin": ",".join(DEV_ORIGINS),
        "Access-Control-Allow-Methods": ",".join(METHODS),
        "Access-Control-Allow-Credentials": "true",
        "X-Requested-With": "*",
    }
