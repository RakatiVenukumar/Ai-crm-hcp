from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HCPBase(BaseModel):
    name: str = Field(..., max_length=255)
    specialization: Optional[str] = Field(default=None, max_length=255)
    hospital: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=255)


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    specialization: Optional[str] = Field(default=None, max_length=255)
    hospital: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=255)


class HCPResponse(HCPBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
