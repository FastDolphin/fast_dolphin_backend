from typeguard import typechecked
from typing import List, Any, Optional
from model import PersonalTrainingWithID
from utils import NotFoundError
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
