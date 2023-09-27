from typing import List

from model.dryland_training_plan import DryLandExercise
from model import ParentTraining
from handlers import handle_write_parent_training

if __name__ == "__main__":
    ######## DRYLAND GYM ##########

    dryland_exercise_0: DryLandExercise = DryLandExercise(
        Name="Суставная разминка",
        nSets=1,
        nReps=1,
        Comments="Выполнить вращение в основных суставах, темп спокойный, размеренный",
    )

    dryland_exercise_1: DryLandExercise = DryLandExercise(
        Name="Быстрая ходьба на беговой дорожке", Time=10, Comments="Постоянный темп"
    )

    dryland_exercise_2: DryLandExercise = DryLandExercise(
        Name="Горизонтальный жим сидя на тренажере",
        nSets=3,
        nReps=15,
        Comments="На вдохе согнуть руки, на выдохе мощно выжать вперед",
    )

    dryland_exercise_3: DryLandExercise = DryLandExercise(
        Name="Вертикальная тяга обратным хватом на блоке",
        nSets=3,
        nReps=15,
        Comments="В нижней точке сводить лопатки",
    )

    dryland_exercise_4: DryLandExercise = DryLandExercise(
        Name="Приседания ноги шире плечь",
        nSets=3,
        nReps=15,
        Comments="Набрать нужное количество повторений за произвольное количество подходов",
    )

    dryland_exercise_5: DryLandExercise = DryLandExercise(
        Name="Ягодичный мостик двумя ногами, плечи на лавке",
        nSets=3,
        nReps=15,
        Comments="в верхней точке сильно напрячь ягодицы и зафиксировать на 1 счет",
    )

    dryland_exercise_6: DryLandExercise = DryLandExercise(
        Name="Гиперэкстензия на фитболе",
        nSets=3,
        nReps=15,
        Comments="В верхней точке свести лопатки и напрячь ягодицы, зафиксировать на 1 счет",
    )

    dryland_exercise_7: DryLandExercise = DryLandExercise(
        Name="Подъем согнутых ног в висе на перекладине",
        nSets=3,
        nReps=10,
        Comments="",
    )
    gym_exercises: List[DryLandExercise] = [
        dryland_exercise_0,
        dryland_exercise_1,
        dryland_exercise_2,
        dryland_exercise_3,
        dryland_exercise_4,
        dryland_exercise_5,
        dryland_exercise_6,
        dryland_exercise_7,
    ]

    parent_training_gym: ParentTraining = ParentTraining(
        Level=1,
        Week=1,
        Day=1,
        inGym=True,
        Exercises=gym_exercises,
    )

    handle_write_parent_training("./gym_training.json", parent_training_gym)
