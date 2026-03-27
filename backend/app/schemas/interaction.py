from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: str = Field(..., max_length=255)
    date: str = Field(..., max_length=50)
    time: Optional[str] = Field(default=None, max_length=50)
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = Field(default=None, max_length=50)
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    summary: Optional[str] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = Field(default=None, max_length=255)
    date: Optional[str] = Field(default=None, max_length=50)
    time: Optional[str] = Field(default=None, max_length=50)
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = Field(default=None, max_length=50)
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    summary: Optional[str] = None


class InteractionResponse(InteractionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
