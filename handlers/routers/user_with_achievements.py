import json
import time
from typing import Optional, List, Dict, Any

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
    if not output.Resources:
        raise NotFoundError()
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output


@router.post("/", response_model=RouterOutput)
def create_user_with_achievements(
    request: Request, user_with_achievements: UserWithAchievements, response: Response
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    logger.info(f"Got request with {json.dumps(user_with_achievements.dict())}")
    logger.info(f"Looking for an achievement with TGid: {user_with_achievements.TGid}")
    existing_user = request.app.userwithachievements_collection.find_one(
        {"TGid": user_with_achievements.TGid}
    )
    logger.info(f"Found existing_user: {json.dumps(existing_user)}")
    years_with_achievements: List[Dict[str, Any]] = existing_user["Years"]
    for year in years_with_achievements:
        if year["Year"] == user_with_achievements.Years[0].Year:
            target_year: int = year["Year"]
            logger.info(f"Found the target year: {year['Year']}")
            target_year_with_achievements: YearWithAchievements = YearWithAchievements(
                **year
            )
            logger.info(f"Initialized target year with achivements: {json.dumps(year)}")
            if (
                user_with_achievements.Years[0].Achievements[0]
                in target_year_with_achievements.Achievements
            ):
                logger.warning(
                    f"Found existing achievement {json.dumps(user_with_achievements.Years[0].Achievements[0].dict())}"
                )
                raise AlreadyExistsError()
            else:
                user_with_achievements_with_id: UserWithAchievements = (
                    UserWithAchievementsWithId(**user_with_achievements)
                )
                target_year_with_achievements.Achievements.append(
                    user_with_achievements.Years[0].Achievements[0]
                )
                for _year in user_with_achievements_with_id.Years:
                    if _year.Year == target_year:
                        user_with_achievements_with_id.Years.pop(_year)
                user_with_achievements_with_id.Years.append(
                    target_year_with_achievements
                )

    # user_with_achievements_with_id = UserWithAchievementsWithId(
    #     **user_with_achievements.dict()
    # )
    encoded_user = jsonable_encoder(user_with_achievements_with_id)
    logger.info(f"Created user with achievements and id: {json.dumps(encoded_user)}")
    uploaded_user_with_achievements = (
        request.app.userwithachievements_collection.insert_one(encoded_user)
    )
    created_user_with_achievements = (
        request.app.userwithachievements_collection.find_one(
            {"_id": uploaded_user_with_achievements.inserted_id}
        )
    )
    logger.info(
        f"Created user with achievements: {json.dumps(created_user_with_achievements)}"
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
