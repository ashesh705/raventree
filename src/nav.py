""" Representation of a NAV value"""

from datetime import date, datetime
from decimal import Decimal
from functools import total_ordering
from typing import Any

from pydantic import BaseModel, Field, validator

_DATE_FORMAT = "%d-%m-%Y"


@total_ordering
class NAV(BaseModel):
    scheme_code: int
    scheme_name: str = ""
    nav_date: date = Field(alias="date")
    nav: Decimal = Field(ge=0)

    @property
    def _key(self) -> tuple[int, date]:
        return self.scheme_code, self.nav_date

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NAV):
            raise ValueError("Cannot compare a NAV object with any other type")

        return self._key == other._key

    def __lt__(self, other: "NAV") -> bool:
        return self._key < other._key

    @validator("nav_date", pre=True)
    def get_nav_date(cls, v: str) -> date:
        return datetime.strptime(v, _DATE_FORMAT).date()
