import uuid
from pydantic import BaseModel, Field
from typing import List, Optional


class Report(BaseModel):
    isInjured: bool = False
    allDaysDone: bool = True
    allExercisesDone: bool = True
    ProblematicExercises: List[str] = []
    Comments: Optional[str] = None
    TgId: int
    Year: int
    Week: int
    TgIdYearWeek: str = ""

    def set_TgIdYearWeek(self) -> None:
        self.TgIdYearWeek = str(self.TgId) + str(self.Year) + str(self.Week)


class ReportWithId(Report):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
