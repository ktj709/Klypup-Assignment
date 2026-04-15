from pydantic import BaseModel

from app.models.entities import Role


class CurrentUser(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None


class TenantContext(BaseModel):
    org_id: int
    role: Role
    user_id: int
