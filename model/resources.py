import uuid
import time
from typing import List, Any, Union, Literal
from pydantic import BaseModel, Field
import datetime
from pyhere import here  # type: ignore
import sys
import re

sys.path.append(str(here().resolve()))


class RouterOutput(BaseModel):
    Resources: List[Any] = []
    StatusMessage: Union[Literal["Success"], Literal["Failure"]] = "Failure"
    ErrorMessage: str = ""


class CustomerRequest(BaseModel):
    Email: str
    Name: str
    Surname: str
    KidsName: str
    KidsSurname: str
    BirthYear: int = 0
    PhoneNumber: str
    numberOfLessonsWeekly: int
    typeOfLessons: str
    SwimmingLevel: str
    canSwim: bool
    hasTakenCourses: bool

    def has_valid_email(self):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.fullmatch(email_regex, self.Email))


class CustomerRequestWithId(CustomerRequest):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")


class CustomerRequestWithIdAndTimeStamp(CustomerRequestWithId):
    TimeStamp: str = str(time.time())

    def convert_unix_timestamp(self) -> "CustomerRequestWithIdAndTimeStamp":
        """Converts a Unix timestamp in seconds to a human-readable datetime string."""
        self.TimeStamp = str(
            datetime.datetime.fromtimestamp(float(self.TimeStamp)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        return self
