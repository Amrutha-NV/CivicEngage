from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class Campaign(BaseModel):
    id: str = Field(..., alias="_id")
    title: str
    description: str
    category: str
    location: str
    required_skills: List[str]
    start_date: Optional[date]
    end_date: Optional[date]
    maximum_volunteers: int
    current_volunteers: int
    status: str
    metadata: Optional[dict] = None

    class Config:
        allow_population_by_field_name = True
        extra = "forbid"
