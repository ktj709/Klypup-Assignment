from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.entities import Role


class MembershipOut(BaseModel):
    id: int
    org_id: int
    user_id: int
    role: Role

    model_config = ConfigDict(from_attributes=True)


class InviteOut(BaseModel):
    id: int
    org_id: int
    code: str
    expires_at: datetime | None
    used_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JoinWithInviteRequest(BaseModel):
    invite_code: str
