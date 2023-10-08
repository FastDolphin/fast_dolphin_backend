import uuid

from pydantic import BaseModel, validator, Field
from typing import Optional, List
import time


class Emergency(BaseModel):
    EmergencyComment: str


class Attendance(BaseModel):
    Attenders: List[str]


class TrainingPlanReport(BaseModel):
    doneEverything: bool
    notDoneVolume: Optional[int] = None
    notDoneVolumeUnits: Optional[str] = None
    Comment: Optional[str] = None

    @validator("notDoneVolumeUnits", pre=True, always=True)
    def check_not_done_volume_units(cls, value):
        if value not in ["м", "мин"]:
            raise ValueError("notDoneVolumeUnits must be either 'сек' or 'мин'")
        return value


class CoachInfo(BaseModel):
    CoachTGId: int
    CoachName: Optional[str] = None
    CoachSurname: Optional[str] = None


class SwimGroupInfo(BaseModel):
    WeekDay: int
    Time: int
    WeekDayTime: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.set_WeekDayTime()

    def set_WeekDayTime(self):
        self.WeekDayTime: str = str(self.WeekDay) + str(self.Time)


class TrainingReport(BaseModel):
    Coach: CoachInfo
    TrainingPlanLevelWeekDay: str
    SwimGroup: SwimGroupInfo
    PlanGroup: str
    TimeStamp: str = str(time.time())
    Emergency: Optional[Emergency] = None
    Attendance: Optional[Attendance] = None
    TrainingPlanReport: TrainingPlanReport

    def __init__(self, **data):
        super().__init__(**data)
        self.set_PlanGroup()

    def set_PlanGroup(self):
        self.PlanGroup = self.TrainingPlanLevelWeekDay + self.SwimGroup.WeekDayTime


class TrainingReportWithId(TrainingReport):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
