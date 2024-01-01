from fastapi.encoders import jsonable_encoder
from typeguard import typechecked
from typing import List, Any, Optional
from model import PersonalTrainingWithID
from utils import NotFoundError, NotMatchedError, NotModifiedError
from starlette.datastructures import Headers


@typechecked
def handle_read_personal_training(
    db: Any,
    headers: Headers,
    tg_id: int,
    year: int,
    week: int,
    day: Optional[int] = None,
) -> List[PersonalTrainingWithID]:
    found_personal_training: List[PersonalTrainingWithID] = []
    if day is not None:
        tg_id_year_week_day: str = str(tg_id) + str(year) + str(week) + str(day)

        existing_personal_training = db.find_one(
            {"TgIdYearWeekDay": tg_id_year_week_day}
        )
        if not existing_personal_training:
            raise NotFoundError()
        found_personal_training.append(
            PersonalTrainingWithID(**existing_personal_training)
        )
        return found_personal_training
    else:
        # If day is not provided, fetch all training plans for the specified level and week
        tg_id_year_week_prefix: str = str(tg_id) + str(year) + str(week)
        matching_personal_trainings = list(
            db.find({"TgIdYearWeekDay": {"$regex": f"^{tg_id_year_week_prefix}"}})
        )
        if not matching_personal_trainings:
            api_key_year_week_prefix: str = (
                str(headers.get("X-Api-Key")) + str(year) + str(week)
            )
            matching_personal_trainings = list(
                db.find(
                    {"ApiKeyYearWeekDay": {"$regex": f"^{api_key_year_week_prefix}"}}
                )
            )
            if not matching_personal_trainings:
                raise NotFoundError(
                    detail="Personal training wasn't found with neither the TgId nor ApiKey."
                )

        for personal_training in matching_personal_trainings:
            found_personal_training.append(PersonalTrainingWithID(**personal_training))
        found_personal_training.sort(key=lambda x: x.Day)
        return found_personal_training


@typechecked
def handle_update_tg_id_in_personal_training(
    db: Any, headers: Headers, tg_id: int, year: int, week: int
):
    api_key_year_week_prefix: str = (
        str(headers.get("X-Api-Key")) + str(year) + str(week)
    )
    matching_personal_trainings = list(
        db.find(
            {"ApiKeyYearWeekDay": {"$regex": f"^{api_key_year_week_prefix}"}, "TgId": 0}
        )
    )
    if not matching_personal_trainings:
        raise NotFoundError()

    old_encoded: List[Any] = []
    new_encoded: List[Any] = []

    for personal_training in matching_personal_trainings:
        old: PersonalTrainingWithID = PersonalTrainingWithID(**personal_training)
        old_encoded.append(jsonable_encoder(old))
        new: PersonalTrainingWithID = old.copy(deep=True)

        new.TgId = tg_id
        new.set_TgIdYearWeekDay()
        new_encoded.append(jsonable_encoder(new))

    for old, new in zip(old_encoded, new_encoded):
        result = db.replace_one(old, new)
        if result.matched_count == 0:
            raise NotMatchedError()
        elif result.modified_count == 0:
            raise NotModifiedError()
    return new_encoded
