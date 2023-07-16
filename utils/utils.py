from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Union, List, Final
from dataclasses import dataclass
from fastapi import status


@dataclass
class Error:
    error: str = None
    error_code: status = None


class ErrorMessages:
    ALREADY_EXISTS: Final[str] = "Already exists!"
    NOT_FOUND: Final[str] = "Not found!"
    OUT_OF_RANGE: Final[str] = "Out of range!"


class ErrorCodes:
    UNPROCESSABLE_ENTITY: Final = status.HTTP_422_UNPROCESSABLE_ENTITY
    ENTITY_NOT_FOUND: Final = status.HTTP_404_NOT_FOUND
    INTERNAL_SERVER_ERROR: Final = status.HTTP_500_INTERNAL_SERVER_ERROR


class ErrorCatcher(ABC):
    @abstractmethod
    def catch(self, resource: BaseModel, known_resources: Union[List[BaseModel], None]):
        pass

    @property
    @abstractmethod
    def error(self):
        pass

    @property
    @abstractmethod
    def status_code(self):
        pass

    @abstractmethod
    def _catch_not_found(self):
        pass
