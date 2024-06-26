from typing import Optional, Dict, Any, List, Literal, Union
from fastapi import APIRouter, Response, status, Request, HTTPException
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
from utils import NotFoundError, AlreadyExistsError, NotModifiedError, NotMatchedError
import logging
from handlers import (
    handle_read_personal_training,
    handle_update_tg_id_in_personal_training,
)
from starlette.datastructures import Headers

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
    try:
        db: Any = request.app.personaltraining_collection
        headers: Headers = request.headers
        personal_trainings: List[
            PersonalTrainingWithID
        ] = handle_read_personal_training(
            db=db, headers=headers, tg_id=tg_id, week=week, year=year, day=day
        )
        output.Resources = personal_trainings
        output.StatusMessage = "Success"
        response.status_code = status.HTTP_200_OK
        return output
    except NotFoundError as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        output.ErrorMessage = e.detail
        return output
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        output.ErrorMessage = str(e)
        return output


@router.put("/telegram_id", response_model=RouterOutput)
async def update_tg_id_in_training_plan(
    request: Request, tg_id: int, year: int, week: int, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    try:
        db: Any = request.app.personaltraining_collection
        headers: Headers = request.headers
        new_encoded: List[Any] = handle_update_tg_id_in_personal_training(
            db, headers, tg_id, year, week
        )
        output.Resources = new_encoded
        output.StatusMessage = "Success"
    except NotFoundError:
        output.ErrorMessage = "Personal training wasn't found with ApiKey."
        output.StatusMessage = status.HTTP_404_NOT_FOUND
    except NotModifiedError as e:
        output.ErrorMessage = e.detail
        response.status_code = status.HTTP_409_CONFLICT
    except NotMatchedError as e:
        output.ErrorMessage = e.detail
        response.status_code = status.HTTP_404_NOT_FOUND
    except Exception as e:
        output.ErrorMessage = str(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return output


@router.post("/", response_model=RouterOutput)
def create_training_plan(
    request: Request, personal_training: PersonalTraining, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    personal_training.set_TgIdYearWeekDay()
    personal_training.set_total_number_of_exercises()
    personal_training.set_total_training_time()
    personal_training.set_total_volume_and_time()

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
    request: Request, id: str, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    delete_result = request.app.personaltraining_collection.delete_one({"_id": id})
    if delete_result.deleted_count == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        output.ErrorMessage = "Personal training is not found."
        return output
    response.status_code = status.HTTP_200_OK
    output.StatusMessage = "Success"
    return output


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

        output.Resources.append(
            PersonalTrainingMetaDataWithID(**personal_training_metadata)
        )
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
    request: Request,
    response: Response,
    tg_id: Optional[int] = None,
    mtdata_id: Optional[str] = None,
) -> Response:
    del_d: Union[Dict[str, int], Dict[str, str]]
    if tg_id:
        del_d = {"TgId": tg_id}

    elif mtdata_id:
        del_d = {"_id": mtdata_id}

    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either telegram id or metadata id should be provided",
        )
    delete_result = request.app.personaltrainingmetadata_collection.delete_one(del_d)
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
