from typing import List

from model.dryland_training_plan import DryLandExercise
from model import ParentTraining
from handlers import handle_write_parent_training

if __name__ == "__main__":
    ######## DRYLAND OUTSIDE ##########

    dryland_exercise_0: DryLandExercise = DryLandExercise(
        Name="Суставная разминка",
        nSets=1,
        nReps=1,
        Comments="Выполнить вращение в основных суставах, темп спокойный, размеренный",
    )

    dryland_exercise_1: DryLandExercise = DryLandExercise(
        Name="Быстрая ходьба", Time=10, Comments="Постоянный темп"
    )

    dryland_exercise_2: DryLandExercise = DryLandExercise(
        Name="Отжимания от пола",
        nSets=1,
        nReps=20,
        Comments="Набрать нужное количество повторений за произвольное количество подходов",
    )

    dryland_exercise_3: DryLandExercise = DryLandExercise(
        Name="Подтягивания на низкой перекладине",
        nSets=3,
        nReps=10,
        Comments="Ноги прямые, туловище напряжено, выполнять касание перекладины с каждым повторением",
    )

    dryland_exercise_4: DryLandExercise = DryLandExercise(
        Name="Приседания ноги шире плечь",
        nSets=1,
        nReps=30,
        Comments="Набрать нужное количество повторений за произвольное количество подходов",
    )

    dryland_exercise_5: DryLandExercise = DryLandExercise(
        Name="Ягодичный мостик двумя ногами, плечи на лавке",
        nSets=3,
        nReps=10,
        Comments="в верхней точке сильно напрячь ягодицы и зафиксировать на 1 счет",
    )

    dryland_exercise_6: DryLandExercise = DryLandExercise(
        Name="Подъем согнутых ног в висе на перекладине",
        nSets=3,
        nReps=10,
        Comments="",
    )
    outside_exercises: List[DryLandExercise] = [
        dryland_exercise_0,
        dryland_exercise_1,
        dryland_exercise_2,
        dryland_exercise_3,
        dryland_exercise_4,
        dryland_exercise_5,
        dryland_exercise_6,
    ]

    parent_training_outside: ParentTraining = ParentTraining(
        Level=1,
        Week=1,
        Day=1,
        inGym=False,
        Exercises=outside_exercises,
    )

    handle_write_parent_training("./outside_training.json", parent_training_outside)
