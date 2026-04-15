from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import OrganizationMembership, User
from app.schemas.auth import CurrentUser, TenantContext


def get_tenant_context(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenantContext:
    user = db.query(User).filter(User.auth0_sub == current_user.sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not provisioned")

    membership = db.query(OrganizationMembership).filter(OrganizationMembership.user_id == user.id).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization membership")

    return TenantContext(org_id=membership.org_id, role=membership.role, user_id=user.id)
