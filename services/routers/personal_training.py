from typing import Optional, Dict, Any, List, Literal
from fastapi import APIRouter, Response, status, Request
from fastapi.encoders import jsonable_encoder
from model import (
    PersonalTraining,
    PersonalTrainingWithID,
    RouterOutput,
    PersonalTrainingMetaDataWithID,
    PersonalTrainingMetaData,
    Report,
    ReportWithId,
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
    existing_personal_training: Dict[str, Any]
    if day is not None:
        tg_id_year_week_day: str = str(tg_id) + str(year) + str(week) + str(day)

        existing_personal_training = request.app.personaltraining_collection.find_one(
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
        matching_personal_trainings = list(matching_personal_trainings)
        if not matching_personal_trainings:
            api_key_year_week_prefix: str = (
                str(request.headers.get("X-Api-Key")) + str(year) + str(week)
            )
            matching_personal_trainings = request.app.personaltraining_collection.find(
                {"ApiKeyYearWeekDay": {"$regex": f"^{api_key_year_week_prefix}"}}
            )
            matching_personal_trainings = list(matching_personal_trainings)
            if not matching_personal_trainings:
                output.ErrorMessage = (
                    "Personal training wasn't found with neither the TgId nor ApiKey."
                )
                output.StatusMessage = "Failure"
                response.status_code = status.HTTP_404_NOT_FOUND
                return output

        for personal_training in matching_personal_trainings:
            output.Resources.append(PersonalTraining(**personal_training))
        output.Resources.sort(key=lambda x: x.Day)

    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.put("/telegram_id", response_model=RouterOutput)
async def update_tg_id_in_training_plan(
    request: Request, tg_id: int, year: int, week: int, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    api_key_year_week_prefix: str = (
        str(request.headers.get("X-Api-Key")) + str(year) + str(week)
    )
    matching_personal_trainings = request.app.personaltraining_collection.find(
        {"ApiKeyYearWeekDay": {"$regex": f"^{api_key_year_week_prefix}"}}
    )
    matching_personal_trainings = list(matching_personal_trainings)
    if not matching_personal_trainings:
        output.ErrorMessage = "Personal training wasn't found with ApiKey."
        output.StatusMessage = "Failure"
        response.status_code = status.HTTP_404_NOT_FOUND
        return output
    personal_trainings_no_tg_id: List[PersonalTrainingWithID] = []
    personal_trainings_with_tg_id: List[PersonalTrainingWithID] = []
    for personal_training in matching_personal_trainings:
        personal_training_no_tg_id: PersonalTrainingWithID = PersonalTrainingWithID(
            **personal_training
        )
        personal_trainings_no_tg_id.append(personal_training_no_tg_id)
        import pdb

        pdb.set_trace()

        personal_training_with_tg_id: PersonalTrainingWithID = (
            personal_training_no_tg_id.copy(deep=True)
        )
        personal_training_with_tg_id.TgId = tg_id
        personal_training_with_tg_id.set_TgIdYearWeekDay()
        personal_trainings_with_tg_id.append(personal_training_with_tg_id)
        for old, new in zip(personal_trainings_no_tg_id, personal_trainings_with_tg_id):
            old_encoded = jsonable_encoder(old)
            new_encoded = jsonable_encoder(new)
            result = request.app.personaltraining_collection.replace_one(
                old_encoded, new_encoded
            )

            if result.matched_count == 0:
                output.ErrorMessage = "No match for API Key."
                response.status_code = status.HTTP_409_CONFLICT
                return output
            elif result.modified_count == 0:
                output.ErrorMessage = "API key was not modified"
                response.status_code = status.HTTP_409_CONFLICT
                return output
            else:
                response.status_code = status.HTTP_200_OK
                output.StatusMessage = "Success"
                output.Resources.append(new)
                output.ErrorMessage = ""
    return output


@router.post("/", response_model=RouterOutput)
def create_training_plan(
    request: Request, personal_training: PersonalTraining, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    personal_training.set_TgIdYearWeekDay()
    personal_training.set_total_number_of_exercises()
    personal_training.set_total_training_time()

    if personal_training.ApiKey:
        personal_training.set_ApiKeyYearWeekDay()

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


###############################
######## METADATA #############
###############################


metadata: Literal["/metadata"] = "/metadata"


@router.get(metadata, response_model=RouterOutput)
def read_personal_training_metadata(
    request: Request,
    tg_id: int,
    response: Response,
    day: Optional[int] = None,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    if day is None:
        metadata_to_find: Dict[str, int] = {"TgId": tg_id}
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


@router.post(metadata, response_model=RouterOutput)
def create_training_plan_metadata(
    request: Request, metadata: PersonalTrainingMetaData, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    metadata_to_create: Dict[str, int] = {"TgId": metadata.TgId}
    existing_training_plan_metadata = (
        request.app.personaltrainingmetadata_collection.find_one(metadata_to_create)
    )
    if existing_training_plan_metadata:
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


@router.delete(metadata, response_model=RouterOutput)
def delete_personal_training_metadata(
    request: Request, tg_id: int, response: Response
) -> Response:
    metadata_to_tg_id: Dict[str, int] = {"TgId": tg_id}
    delete_result = request.app.personaltrainingmetadata_collection.delete_one(
        metadata_to_tg_id
    )
    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise NotFoundError()


###############################
######## REPORT ###############
###############################

report: Literal["/report"] = "/report"


@router.get(report, response_model=RouterOutput)
def read_personal_training_report(
    request: Request,
    tg_id: int,
    year: int,
    week: int,
    response: Response,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    tg_id_year_week: str = str(tg_id) + str(year) + str(week)

    report_to_find: Dict[str, str] = {"TgIdYearWeek": tg_id_year_week}
    personal_training_report: Dict[
        str, Any
    ] = request.app.personaltrainingreport_collection.find_one(report_to_find)

    if not personal_training_report:
        raise NotFoundError()

    output.Resources.append(Report(**personal_training_report))
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post(report, response_model=RouterOutput)
def create_training_plan_report(
    request: Request, report: Report, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    report.set_TgIdYearWeek()

    report_to_create: Dict[str, str] = {"TgIdYearWeek": report.TgIdYearWeek}
    existing_report = request.app.personaltrainingreport_collection.find_one(
        report_to_create
    )
    if existing_report:
        raise AlreadyExistsError()

    report_with_id: ReportWithId = ReportWithId(**report.dict())
    encoded_report_with_id = jsonable_encoder(report_with_id)

    uploaded_report = request.app.personaltrainingreport_collection.insert_one(
        encoded_report_with_id
    )
    created_report = request.app.personaltrainingreport_collection.find_one(
        {"_id": uploaded_report.inserted_id}
    )

    output.Resources.append(created_report)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.delete(report, response_model=RouterOutput)
def delete_personal_training_report(
    request: Request, tg_id: int, year: int, week: int, response: Response
) -> Response:
    tg_id_year_week: str = str(tg_id) + str(year) + str(week)
    report_to_delete: Dict[str, str] = {"TgIdYearWeek": tg_id_year_week}
    delete_result = request.app.personaltrainingreport_collection.delete_one(
        report_to_delete
    )
    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise NotFoundError()
