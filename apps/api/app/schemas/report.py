from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    query_text: str = Field(min_length=3)
    summary: str | None = None


class ReportUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    summary: str | None = None


class ReportOut(BaseModel):
    id: int
    org_id: int
    title: str
    query_text: str
    status: str
    summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
