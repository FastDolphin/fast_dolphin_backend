from fastapi import HTTPException


class WrongEmailFormat(HTTPException):
    def __init__(self):
        detail = f"The email has an invalid format."
        super().__init__(status_code=400, detail=detail)


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Not found."):
        super().__init__(status_code=404, detail=detail)


class NotUpdatedError(HTTPException):
    def __init__(self):
        detail = "Not updated error."
        super().__init__(status_code=500, detail=detail)


class AlreadyExistsError(HTTPException):
    def __init__(self):
        detail = "Already exists."
        super().__init__(status_code=409, detail=detail)
