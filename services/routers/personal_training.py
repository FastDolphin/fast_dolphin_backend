from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Response, status, Request
from fastapi.encoders import jsonable_encoder
from model import (
    PersonalTraining,
    PersonalTrainingWithID,
    RouterOutput,
    PersonalTrainingMetaDataWithID,
    PersonalTrainingMetaData,
)
from utils import NotFoundError, AlreadyExistsError
import logging

router = APIRouter(prefix="/v1/personal-training", tags=["personal-training"])
logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/", response_model=RouterOutput)
def read_personal_training(
    request: Request,
    tg_id: int,
    year: int,
    week: int,
    response: Response,
    day: Optional[int] = None,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    if day is not None:
        tg_id_year_week_day: str = str(tg_id) + str(year) + str(week) + str(day)

        existing_personal_training: Dict[
            str, Any
        ] = request.app.personaltraining_collection.find_one(
            {"TgIdYearWeekDay": tg_id_year_week_day}
        )

        if not existing_personal_training:
            raise NotFoundError()

        output.Resources.append(PersonalTraining(**existing_personal_training))
    else:
        # If day is not provided, fetch all training plans for the specified level and week
        tg_id_year_week_prefix: str = str(tg_id) + str(year) + str(week)
        matching_personal_trainings = request.app.personaltraining_collection.find(
            {"TgIdYearWeekDay": {"$regex": f"^{tg_id_year_week_prefix}"}}
        )
        if not matching_personal_trainings:
            raise NotFoundError()

        for personal_training in matching_personal_trainings:
            output.Resources.append(PersonalTraining(**personal_training))
        output.Resources.sort(key=lambda x: x.Day)

    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post("/", response_model=RouterOutput)
def create_training_plan(
    request: Request, personal_training: PersonalTraining, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    personal_training.set_TgIdYearWeekDay()
    personal_training.set_total_number_of_exercises()
    personal_training.set_total_training_time()

    existing_training_plan = request.app.personaltraining_collection.find_one(
        {"TgIdYearWeekDay": personal_training.TgIdYearWeekDay}
    )

    if existing_training_plan:
        raise AlreadyExistsError()

    personal_training_with_id = PersonalTrainingWithID(**personal_training.dict())

    encoded_personal_training = jsonable_encoder(personal_training_with_id)

    uploaded_personal_training = request.app.personaltraining_collection.insert_one(
        encoded_personal_training
    )
    created_personal_training = request.app.personaltraining_collection.find_one(
        {"_id": uploaded_personal_training.inserted_id}
    )

    output.Resources.append(created_personal_training)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.delete("/", response_model=RouterOutput)
def delete_personal_training(
    request: Request, tg_id: int, year: int, week: int, day: int, response: Response
) -> Response:
    tg_id_year_week_day: str = str(tg_id) + str(year) + str(week) + str(day)

    delete_result = request.app.personaltraining_collection.delete_one(
        {"TgIdLevelWeekDay": tg_id_year_week_day}
    )

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise NotFoundError()


@router.get("/all", response_model=RouterOutput)
async def read_all_personal_trainings(
    request: Request, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    personal_trainings: List[Dict[str, Any]] = list(
        request.app.personaltraining_collection.find(limit=100)
    )

    output.Resources = [
        PersonalTraining(**personal_training)
        for personal_training in personal_trainings
    ]
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.get("/metadata", response_model=RouterOutput)
def read_personal_training_metadata(
    request: Request,
    tg_id: int,
    response: Response,
    day: Optional[int] = None,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    if day is not None:
        metadata_to_find: Dict[str, str] = {"TgId": str(tg_id)}
        personal_training_metadata: Dict[
            str, Any
        ] = request.app.personaltrainingmetadata_collection.find_one(metadata_to_find)

        if not personal_training_metadata:
            raise NotFoundError()

        output.Resources.append(PersonalTrainingMetaData(**personal_training_metadata))
    else:
        raise NotImplementedError

    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post("/metadata", response_model=RouterOutput)
def create_training_plan_metadata(
    request: Request, metadata: PersonalTrainingMetaData, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    metadata_to_create: Dict[str, str] = {"TgId": str(metadata.TgId)}
    existing_training_plan = request.app.personaltrainingmetadata_collection.find_one(
        metadata_to_create
    )
    if existing_training_plan:
        raise AlreadyExistsError()

    metadata_with_id: PersonalTrainingMetaDataWithID = PersonalTrainingMetaDataWithID(
        **metadata.dict()
    )
    encoded_metadata_with_id = jsonable_encoder(metadata_with_id)

    uploaded_metadata = request.app.personaltrainingmetadata_collection.insert_one(
        encoded_metadata_with_id
    )
    created_metadata = request.app.personaltrainingmetadata_collection.find_one(
        {"_id": uploaded_metadata.inserted_id}
    )

    output.Resources.append(created_metadata)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.delete("/metadata", response_model=RouterOutput)
def delete_personal_training_metadata(
    request: Request, tg_id: int, response: Response
) -> Response:
    metadata_to_tg_id: Dict[str, str] = {"TgId": str(tg_id)}
    delete_result = request.app.personaltrainingmetadata_collection.delete_one(
        metadata_to_tg_id
    )
    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise NotFoundError()
