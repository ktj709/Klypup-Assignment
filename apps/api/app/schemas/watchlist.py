from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WatchlistCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)
    company_name: str | None = Field(default=None, max_length=255)


class WatchlistOut(BaseModel):
    id: int
    org_id: int
    ticker: str
    company_name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
