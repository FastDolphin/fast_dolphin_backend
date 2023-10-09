from fastapi import APIRouter, Response, status, Request
from typing import List
from pyhere import here
import sys
import json
import pika
from handlers import prepare_report_with_id_if_not_existent
import logging
from model import (
    RouterOutput,
    TrainingReport,
    TrainingReportWithId,
)
from dotenv import dotenv_values
from utils import NotFoundError

sys.path.append(str(here().resolve()))
config = dotenv_values(".env")
ROUTING_KEY: str = config.get("ROUTING_KEY")

logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


router = APIRouter(prefix="/v1/training-report", tags=["training report"])


@router.post("/", response_model=RouterOutput)
async def create_training_report(
    new_training_report: TrainingReport, response: Response, request: Request
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    existent_reports = list(
        request.app.requests_collection.find(
            {"PlanGroup": new_training_report.PlanGroup}
        )
    )
    encoded_new_report_with_id = prepare_report_with_id_if_not_existent(
        existent_reports=existent_reports, new_report=new_training_report
    )
    uploaded_report = request.app.reports_collection.insert_one(
        encoded_new_report_with_id
    )
    created_report = request.app.reports_collection.find_one(
        {"_id": uploaded_report.inserted_id}
    )

    output.Resources.append(TrainingReportWithId(**created_report))
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK

    encoded_new_report_with_id_str: str = json.dumps(encoded_new_report_with_id)
    MAX_RETRIES: int = 5
    for attempt in range(MAX_RETRIES):
        try:
            # Check if the connection and channel are open
            if (
                not request.app.rabbitmq_connection.is_open
                or not request.app.rabbitmq_channel.is_open
            ):
                # Log the state
                logging.warning(
                    "RabbitMQ connection or channel is closed. Attempting to reconnect..."
                )
                logger.info("Trying to re-establish the connection...")
                # Re-establish the connection and channel
                request.app.rabbitmq_connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host="rabbitmq")
                )
                request.app.rabbitmq_channel = request.app.rabbitmq_connection.channel()

            logger.info(
                f"Trying to publish: \n"
                f"{encoded_new_report_with_id_str}\n"
                f"with routing_key {ROUTING_KEY}"
            )
            request.app.rabbitmq_channel.basic_publish(
                exchange="",
                routing_key=ROUTING_KEY,
                body=encoded_new_report_with_id_str,
            )
            break  # If successful, exit the loop
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}: Error publishing to RabbitMQ: {e}")
            if attempt == MAX_RETRIES - 1:
                # After all retries, if still unsuccessful
                # Additional error handling can be done here, like raising a custom exception
                raise Exception(
                    f"Failed to publish to RabbitMQ after {MAX_RETRIES} attempts."
                )

    return output


@router.get("/all", response_model=List[TrainingReportWithId])
async def read_all_reports(
    request: Request,
) -> List[TrainingReportWithId]:
    all_reports = request.app.reports_collection.find()
    return [TrainingReportWithId(**request) for request in all_reports]


@router.delete("/{id}", response_model=RouterOutput)
async def delete_report(id: str, request: Request, response: Response) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    existing_report = request.app.reports_collection.find_one({"_id": id})
    if not existing_report:
        raise NotFoundError()
    existing_repost_with_id: TrainingReportWithId = TrainingReportWithId(
        **existing_report
    )
    result = request.app.reports_collection.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise NotFoundError()
    elif result.deleted_count == 1:
        output.Resources.append(existing_repost_with_id)
        output.StatusMessage = "Success"
        response.status_code = status.HTTP_200_OK
        return output
    else:
        output.StatusMessage = "Success"
        response.status_code = status.HTTP_200_OK
        return output
