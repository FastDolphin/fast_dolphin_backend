import os
from typing import List


def handle_paths(outside_training_path: str, gym_training_path: str) -> List[str]:
    if not os.path.exists(outside_training_path):
        outside_training_path = "parent_training/parent_training.json"

    if not os.path.exists(gym_training_path):
        gym_training_path = "parent_training/gym_parent_training.json"

    paths: List[str] = [outside_training_path, gym_training_path]
    if any(not os.path.exists(p) for p in paths):
        raise FileNotFoundError
    return paths
