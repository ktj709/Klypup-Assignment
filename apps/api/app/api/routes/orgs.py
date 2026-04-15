from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import OrganizationInvite, OrganizationMembership, Role
from app.schemas.auth import TenantContext
from app.schemas.org import InviteOut, JoinWithInviteRequest, MembershipOut

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.get("/members", response_model=list[MembershipOut])
def list_members(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[OrganizationMembership]:
    members = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.org_id == tenant.org_id)
        .order_by(OrganizationMembership.id.asc())
        .all()
    )
    return members


@router.post("/invites", response_model=InviteOut, status_code=status.HTTP_201_CREATED)
def create_invite(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> OrganizationInvite:
    if tenant.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create invites")

    invite = OrganizationInvite(
        org_id=tenant.org_id,
        created_by_user_id=tenant.user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.post("/join", response_model=MembershipOut)
def join_with_invite(
    payload: JoinWithInviteRequest,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> OrganizationMembership:
    invite = (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.code == payload.invite_code)
        .first()
    )
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")

    if invite.used_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite code already used")

    if invite.expires_at is not None and invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite code expired")

    existing = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.org_id == invite.org_id, OrganizationMembership.user_id == tenant.user_id)
        .first()
    )
    if existing:
        return existing

    membership = OrganizationMembership(
        org_id=invite.org_id,
        user_id=tenant.user_id,
        role=Role.ANALYST,
    )
    invite.used_at = datetime.now(timezone.utc)
    # The current user can join another organization through a valid invite code.
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
