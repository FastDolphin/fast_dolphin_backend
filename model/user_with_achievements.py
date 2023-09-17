import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class Achievement(BaseModel):
    Distance: int
    Stroke: str
    Date: str
    TimeAchievement: str


class YearWithAchievements(BaseModel):
    Year: int
    Achievements: List[Achievement] = None


class UserWithAchievements(BaseModel):
    TGid: int
    Name: str
    Surname: str
    YearOfBirth: int
    YearsWithAchievements: Optional[List[YearWithAchievements]] = None


class UserWithAchievementsWithId(UserWithAchievements):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
