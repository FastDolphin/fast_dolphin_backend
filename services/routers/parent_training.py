from handlers import handle_read_parent_training, handle_paths
from fastapi import APIRouter, Response, status, Request
from model import ParentTraining, RouterOutput


import logging

router = APIRouter(prefix="/v1/parent-training", tags=["parent-training"])
logging.basicConfig(
    format="%(asctime)s %(message)s", level=logging.DEBUG, datefmt="%d-%b-%y %H:%M"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

EASY_PARENT_TRAINING_PATH: str = "../../parent_training/parent_training.json"
EASY_GYM_PARENT_TRAINING_PATH: str = "../../parent_training/gym_parent_training.json"

EASY_PARENT_TRAINING_PATH, EASY_GYM_PARENT_TRAINING_PATH = handle_paths(
    EASY_PARENT_TRAINING_PATH, EASY_GYM_PARENT_TRAINING_PATH
)


@router.get("/", response_model=RouterOutput)
def read_parent_training(
    request: Request,
    response: Response,
    is_gym: bool,
) -> RouterOutput:
    output = RouterOutput(StatusMessage="Failure")
    parent_training_path = EASY_PARENT_TRAINING_PATH
    if is_gym:
        parent_training_path = EASY_GYM_PARENT_TRAINING_PATH
    parent_training: ParentTraining = handle_read_parent_training(parent_training_path)
    output.Resources.append(parent_training)
    output.StatusMessage = "Success"
    response.status_code = status.HTTP_200_OK
    return output
