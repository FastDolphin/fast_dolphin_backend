import json
import typing
from fastapi.responses import JSONResponse
from .cors_constants import CorsConstants


class ResponseWithCorsHeaders(JSONResponse):
    def __init__(self, content: typing.Any = None, status_code: int = 200):
        super().__init__(content, status_code)

    def add_cors_headers(self, cors_headers: dict = CorsConstants().FULL_HEADERS):
        for _k, _v in cors_headers.items():
            self.headers[_k] = _v

        return self

    def set_body(self, content: dict):
        self.body = json.dumps(
            content,
            cls=json.JSONEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode(self.charset)
        self._update_content_length()

    def _update_content_length(self):
        if "content-length" in self.headers.keys():
            self.headers["content-length"] = str(len(self.body))
