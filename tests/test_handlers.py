import pytest
from handlers import handle_read_parent_training
from model import ParentTraining
from model.dryland_training_plan import DryLandExercise


@pytest.fixture
def test_parent_training_path():
    return "parent_training/parent_training.json"


def test_read_parent_training(test_parent_training_path):
    parent_training: ParentTraining = handle_read_parent_training(
        test_parent_training_path
    )
    assert isinstance(parent_training, ParentTraining)
    for exercise in parent_training.Exercises:
        assert isinstance(exercise, DryLandExercise)
    assert parent_training.TotalNumberExercises > 0
    assert parent_training.TotalTime > 0
