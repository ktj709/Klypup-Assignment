from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import OrganizationInvite, OrganizationMembership, Role
from app.schemas.auth import TenantContext
from app.schemas.org import InviteOut, JoinWithInviteRequest, MembershipOut
from app.services.supabase_rest import get_supabase_rest_client

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.get("/members", response_model=list[MembershipOut])
def list_members(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[OrganizationMembership]:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        return supabase.select(
            "organization_memberships",
            {
                "select": "id,org_id,user_id,role",
                "org_id": f"eq.{tenant.org_id}",
                "order": "id.asc",
            },
        )

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
    settings = get_settings()
    if tenant.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create invites")

    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        invite_payload = {
            "org_id": tenant.org_id,
            "created_by_user_id": tenant.user_id,
            "code": secrets.token_urlsafe(24),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        }
        inserted = supabase.insert(
            "organization_invites",
            invite_payload,
            select="id,org_id,code,expires_at,used_at,created_at",
        )
        return inserted[0]

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
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()
        invite_rows = supabase.select(
            "organization_invites",
            {
                "select": "id,org_id,code,expires_at,used_at",
                "code": f"eq.{payload.invite_code}",
                "limit": "1",
            },
        )
        if not invite_rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")

        invite = invite_rows[0]
        if invite.get("used_at") is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite code already used")

        expires_at = invite.get("expires_at")
        if expires_at:
            expires_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if expires_dt < datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite code expired")

        existing = supabase.select(
            "organization_memberships",
            {
                "select": "id,org_id,user_id,role",
                "org_id": f"eq.{invite['org_id']}",
                "user_id": f"eq.{tenant.user_id}",
                "limit": "1",
            },
        )
        if existing:
            return existing[0]

        inserted_membership = supabase.insert(
            "organization_memberships",
            {
                "org_id": invite["org_id"],
                "user_id": tenant.user_id,
                "role": Role.ANALYST.value,
            },
            select="id,org_id,user_id,role",
        )
        supabase.update(
            "organization_invites",
            {"used_at": datetime.now(timezone.utc).isoformat()},
            {"id": f"eq.{invite['id']}"},
            select="id",
        )
        return inserted_membership[0]

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
