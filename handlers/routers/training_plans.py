import time
from fastapi import APIRouter, Response, status, Request
from fastapi.encoders import jsonable_encoder
from model import TrainingPlan, RouterOutput
from utils import NotFoundError, AlreadyExistsError


import logging

router = APIRouter(prefix="/v1/training-plan", tags=["training-plan"])
logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/", response_model=RouterOutput)
def read_training_plan(
    request: Request, level: int, week: int, day: int, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    level_week_day: str = str(level) + str(week) + str(day)

    existing_training_plan = request.app.trainingplans_collection.find_one(
        {"LevelWeekDay": level_week_day}
    )

    if not existing_training_plan:
        raise NotFoundError()

    output.Resources.append(TrainingPlan(**existing_training_plan))
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post("/", response_model=RouterOutput)
def create_training_plan(
    request: Request, training_plan: TrainingPlan, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    training_plan.set_LevelWeekDay()

    existing_training_plan = request.app.database.TrainingPlans.find_one(
        {"LevelWeekDay": training_plan.LevelWeekDay}
    )

    if existing_training_plan:
        raise AlreadyExistsError()

    encoded_training_plan = jsonable_encoder(training_plan)

    uploaded_training_plan = request.app.database.TrainingPlans.insert_one(
        encoded_training_plan
    )
    created_training_plan = request.app.database.TrainingPlans.find_one(
        {"_id": uploaded_training_plan.inserted_id}
    )

    output.Resources.append(created_training_plan)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.delete("/", response_model=RouterOutput)
def delete_training_plan(
    request: Request, level: int, week: int, day: int, response: Response
) -> Response:
    level_week_day: str = str(level) + str(week) + str(day)

    delete_result = request.app.database.TrainingPlans.delete_one(
        {"LevelWeekDay": level_week_day}
    )

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise NotFoundError()


@router.get("/all", response_model=RouterOutput)
async def read_all_training_plans(request: Request, response: Response) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    training_plans = list(request.app.database.TrainingPlans.find(limit=100))

    if not training_plans:
        raise NotFoundError()

    output.Resources = [
        TrainingPlan(**training_plan) for training_plan in training_plans
    ]
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output
