import time
from typing import Optional

from fastapi import APIRouter, Response, status, Request
from fastapi.encoders import jsonable_encoder
from model import TrainingPlan, RouterOutput, TrainingPlanWithId
from utils import NotFoundError, AlreadyExistsError, NotUpdatedError


import logging

router = APIRouter(prefix="/v1/training-plan", tags=["training-plan"])
logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/", response_model=RouterOutput)
def read_training_plan(
    request: Request,
    level: int,
    week: int,
    response: Response,
    day: Optional[int] = None,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    if day is not None:
        level_week_day: str = str(level) + str(week) + str(day)

        existing_training_plan = request.app.trainingplans_collection.find_one(
            {"LevelWeekDay": level_week_day}
        )

        if not existing_training_plan:
            raise NotFoundError()

        output.Resources.append(TrainingPlan(**existing_training_plan))
    else:
        # If day is not provided, fetch all training plans for the specified level and week
        level_week_prefix: str = str(level) + str(week)
        matching_training_plans = request.app.trainingplans_collection.find(
            {"LevelWeekDay": {"$regex": f"^{level_week_prefix}"}}
        )
        if not matching_training_plans:
            raise NotFoundError()

        matching_training_plans.sort(key=lambda x: x['Day'])
        for training_plan in matching_training_plans:
            output.Resources.append(TrainingPlan(**training_plan))

    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post("/", response_model=RouterOutput)
def create_training_plan(
    request: Request, training_plan: TrainingPlan, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    training_plan.set_LevelWeekDay()
    training_plan.set_total_volume_and_time()

    existing_training_plan = request.app.trainingplans_collection.find_one(
        {"LevelWeekDay": training_plan.LevelWeekDay}
    )

    if existing_training_plan:
        raise AlreadyExistsError()

    training_plan_with_id = TrainingPlanWithId(**training_plan.dict())

    encoded_training_plan = jsonable_encoder(training_plan_with_id)

    uploaded_training_plan = request.app.trainingplans_collection.insert_one(
        encoded_training_plan
    )
    created_training_plan = request.app.trainingplans_collection.find_one(
        {"_id": uploaded_training_plan.inserted_id}
    )

    output.Resources.append(created_training_plan)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.put("/", response_model=RouterOutput)
def update_training_plan(
    request: Request, training_plan: TrainingPlan, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    training_plan.set_LevelWeekDay()
    training_plan.set_total_volume_and_time()

    existing_training_plan = request.app.trainingplans_collection.find_one(
        {"LevelWeekDay": training_plan.LevelWeekDay}
    )

    if not existing_training_plan:
        raise NotFoundError()

    updated_training_plan_with_id = TrainingPlanWithId(**training_plan.dict())
    updated_training_plan_with_id.id = existing_training_plan["_id"]
    encoded_updated_training_plan = jsonable_encoder(updated_training_plan_with_id)
    encoded_existing_training_plan = jsonable_encoder(existing_training_plan)

    result = request.app.trainingplans_collection.replace_one(
        encoded_existing_training_plan, encoded_updated_training_plan
    )
    if result.matched_count == 0:
        raise NotFoundError()
    elif result.modified_count == 0:
        raise NotUpdatedError()
    else:
        updated_training_plan = request.app.trainingplans_collection.find_one(
            {"_id": encoded_existing_training_plan["_id"]}
        )
    output.Resources.append(updated_training_plan)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.delete("/", response_model=RouterOutput)
def delete_training_plan(
    request: Request, level: int, week: int, day: int, response: Response
) -> Response:
    level_week_day: str = str(level) + str(week) + str(day)

    delete_result = request.app.trainingplans_collection.delete_one(
        {"LevelWeekDay": level_week_day}
    )

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise NotFoundError()


@router.get("/all", response_model=RouterOutput)
async def read_all_training_plans(request: Request, response: Response) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    training_plans = list(request.app.trainingplans_collection.find(limit=100))

    output.Resources = [
        TrainingPlan(**training_plan) for training_plan in training_plans
    ]
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output
