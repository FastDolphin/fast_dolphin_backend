import json
from typing import Dict, Any

# from typeguard import typechecked
from model import ParentTraining


def handle_read_parent_training(parent_training_path: str) -> ParentTraining:
    with open(parent_training_path, "r") as file:
        parent_training_dict: Dict[str, Any] = json.load(file)
        parent_training: ParentTraining = ParentTraining(**parent_training_dict)
        parent_training.set_total_number_of_exercises()
        parent_training.set_total_training_time()
        return parent_training


def handle_write_parent_training(
    parent_training_path: str, parent_training: ParentTraining
) -> None:
    parent_training_dump: Dict[str, Any] = json.dumps(parent_training.dict())
    with open(parent_training_path, "w") as file:
        file.write(parent_training_dump)
