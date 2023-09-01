from dataclasses import dataclass
from typing import Final, Tuple


@dataclass
class CorsConstants:
    DEV_ORIGINS: Final[Tuple[str]] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://65.21.50.112:3000",
        "https://65.21.50.112:3000",
        "https://fast-dolphin.com",
        "https://www.fast-dolphin.com",
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
