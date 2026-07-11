from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Volunteer(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    email: Optional[str]
    location: str
    skills: List[str]
    availability: List[str]
    attendance_rate: float
    social_impact_score: float
    verified: bool
    active_campaigns: int
    history_ids: List[str] = []
    metadata: Optional[dict] = None

    class Config:
        allow_population_by_field_name = True
        extra = "forbid"
