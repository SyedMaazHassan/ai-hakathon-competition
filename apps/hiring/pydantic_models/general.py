from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import calendar

from apps.hiring.choices.general import *


class DateModel(BaseModel):
    """Flexible date model to handle partial dates (year-only, year+month, full date)"""

    year: Optional[int] = Field(None, ge=1900, le=2100, description="Year (e.g., 2023)")
    month: Optional[int] = Field(None, ge=1, le=12, description="Month (1–12)")
    day: Optional[int] = Field(None, ge=1, le=31, description="Day (1–31)")
    original: Optional[str] = Field(None, description="Verbatim string from resume (e.g., 'May 2021')")

    def as_date(self) -> Optional[date]:
        """Return full datetime.date if all parts are present"""
        if self.year and self.month and self.day:
            return date(self.year, self.month, self.day)
        return None

    def to_iso(self) -> Optional[str]:
        """Return ISO date string if full date available"""
        d = self.as_date()
        return d.isoformat() if d else None

    def granularity(self) -> str:
        if self.day is not None:
            return "day"
        if self.month is not None:
            return "month"
        if self.year is not None:
            return "year"
        return "none"

    def display_string(self) -> str:
        """Human-readable display"""
        if not self.year:
            return ""
        if not self.month:
            return str(self.year)
        month_name = calendar.month_name[self.month]
        if not self.day:
            return f"{month_name} {self.year}"
        return f"{month_name} {self.day}, {self.year}"

    def __str__(self) -> str:
        return self.display_string()

