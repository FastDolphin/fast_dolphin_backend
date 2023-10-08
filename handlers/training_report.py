from fastapi.encoders import jsonable_encoder
from model import TrainingReport, TrainingReportWithId
from typing import Any
from utils import AlreadyExistsError


def prepare_report_with_id_if_not_existent(
    existent_reports, new_report: TrainingReport
) -> Any:
    if existent_reports:
        raise AlreadyExistsError()

    new_report_with_id: TrainingReportWithId = TrainingReportWithId(**new_report.dict())
    encoded_new_report_with_id = jsonable_encoder(new_report_with_id)
    return encoded_new_report_with_id
