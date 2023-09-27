from typing import List

from model import ParentTraining
from model.dryland_training_plan import DryLandExercise
import pytest

#
# class DryLandExercise(BaseModel):
#     Name: str
#     nSets: float
#     nReps: float
#     Time: Optional[float] = None
#     TimeUnits: str = "мин"
#     Weight: float = 0.0
#     WeightUnits: str = "кг"
#     OtherResistance: Optional[str] = None
#     ResistanceComments: Optional[str] = None
#     Speed: Optional[int] = None
#     Comments: Optional[str] = None
#     TotalExerciseTime: float = 0.0
#
#     _AverageRepTime: int = 3
#     _AverageRepTimeUnits: str = "сек"
#     _AverageRestTime: int = 60
#     _AverageRestTimeUnits: str = "сек"


#
# class ParentTraining(BaseModel):
#     LevelWeekDay: str = None
#     Level: int
#     Week: int
#     Day: int
#     inGym: bool
#     Exercises: List[DryLandExercise]
#     TotalNumberExercises: int = 0
#     TotalTime: float = 0.0
@pytest.fixture
def test_n_sets() -> int:
    return 3


@pytest.fixture
def test_n_reps() -> int:
    return 10


@pytest.fixture
def test_time_min() -> int:
    return 10


@pytest.fixture
def test_dryland_exercise_no_time(test_n_sets, test_n_reps) -> DryLandExercise:
    dryland_exercise: DryLandExercise = DryLandExercise(
        Name="Суставная разминка",
        nSets=test_n_sets,
        nReps=test_n_reps,
        Comments="Выполнить вращение в основных суставах, темп спокойный, размеренный",
    )
    return dryland_exercise


@pytest.fixture
def test_dryland_exercise_with_time(test_time_min) -> DryLandExercise:
    dryland_exercise: DryLandExercise = DryLandExercise(
        Name="Быстрая ходьба", Time=test_time_min, Comments="Постоянный темп"
    )
    return dryland_exercise


@pytest.fixture
def test_exercises(
    test_dryland_exercise_no_time, test_dryland_exercise_with_time
) -> List[DryLandExercise]:
    return [test_dryland_exercise_with_time, test_dryland_exercise_no_time]


@pytest.fixture
def test_parent_training(test_exercises) -> ParentTraining:
    parent_training: ParentTraining = ParentTraining(
        Level=1,
        Week=1,
        Day=1,
        inGym=False,
        Exercises=test_exercises,
    )
    return parent_training


def test_set_total_time_exercise_no_time(
    test_dryland_exercise_no_time, test_n_reps, test_n_sets
):
    test_dryland_exercise_no_time.set_total_exercise_time()
    one_set_and_rest_time: float = (
        test_dryland_exercise_no_time._AverageRepTime * test_n_reps
        + test_dryland_exercise_no_time._AverageRestTime
    )
    assert (
        test_dryland_exercise_no_time.TotalExerciseTime
        == one_set_and_rest_time * test_n_sets
    )


def test_set_total_time_exercise_with_time_min(
    test_dryland_exercise_with_time, test_time_min
):
    test_dryland_exercise_with_time.set_total_exercise_time()
    one_set_and_rest_time: float = (
        test_time_min * 60 + test_dryland_exercise_with_time._AverageRestTime
    )
    assert test_dryland_exercise_with_time.TotalExerciseTime == one_set_and_rest_time


def test_total_n_exercise_parent_training(test_parent_training, test_exercises):
    test_parent_training.set_total_number_of_exercises()
    assert test_parent_training.TotalNumberExercises == len(test_exercises)


def test_total_time_parent_training(test_parent_training, test_exercises):
    exercise_time: float = 0.0
    for exercise in test_exercises:
        exercise.set_total_exercise_time()
        exercise_time += exercise.TotalExerciseTime

    test_parent_training.set_total_training_time()
    assert test_parent_training.TotalTime == exercise_time
