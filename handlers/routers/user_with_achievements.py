import time
from typing import Optional

from fastapi import APIRouter, Response, status, Request
from fastapi.encoders import jsonable_encoder
from model import (
    Achievement,
    YearWithAchievements,
    UserWithAchievements,
    UserWithAchievementsWithId,
    RouterOutput,
)
from utils import NotFoundError, AlreadyExistsError

import logging

router = APIRouter(prefix="/v1/user-with-achievements", tags=["user-with-achievements"])
logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/", response_model=RouterOutput)
def read_user_with_achievements(
    request: Request,
    tg_id: int,
    distance: int,
    stroke: str,
    response: Response,
    target_year: Optional[int] = None,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")

    existing_user_with_achievements = (
        request.app.userwithachievements_collection.find_one({"TGid": tg_id})
    )
    if not existing_user_with_achievements:
        raise NotFoundError()
    user = UserWithAchievements(**existing_user_with_achievements)

    if target_year is not None:
        for year_with_achievements in user.Years:
            if year_with_achievements.Year == target_year:
                if year_with_achievements.Achievements:
                    for achievement in year_with_achievements.Achievements:
                        if (
                            achievement.Stroke == stroke
                            and achievement.Distance == distance
                        ):
                            output.Resources.append(achievement)
                else:
                    raise NotFoundError()
    else:
        raise NotImplementedError
    if not response.Resources:
        raise NotFoundError()
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post("/", response_model=RouterOutput)
def create_user_with_achievements(
    request: Request, user_with_achievements: UserWithAchievements, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    existing_user = request.app.userwithachievements_collection.find_one(
        {"TGid": user_with_achievements.TGid}
    )
    if existing_user:
        raise AlreadyExistsError()

    user_with_achievements_with_id = UserWithAchievementsWithId(
        **user_with_achievements.dict()
    )
    encoded_user = jsonable_encoder(user_with_achievements_with_id)
    uploaded_user_with_achievements = (
        request.app.userwithachievements_collection.insert_one(encoded_user)
    )
    created_user_with_achievements = (
        request.app.userwithachievements_collection.find_one(
            {"_id": uploaded_user_with_achievements.inserted_id}
        )
    )
    output.Resources.append(created_user_with_achievements)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.delete("/", response_model=RouterOutput)
def delete_user_with_achievements(
    request: Request, tg_id: int, response: Response
) -> Response:
    delete_result = request.app.userwithachievements_collection.delete_one(
        {"TGid": tg_id}
    )
    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    raise NotFoundError()
