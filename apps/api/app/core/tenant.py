from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import OrganizationMembership, Role, User
from app.schemas.auth import CurrentUser, TenantContext
from app.services.supabase_rest import get_supabase_rest_client


def get_tenant_context(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenantContext:
    settings = get_settings()
    if settings.data_backend == "supabase_rest":
        supabase = get_supabase_rest_client()

        users = supabase.select(
            "users",
            {
                "select": "id",
                "auth0_sub": f"eq.{current_user.sub}",
                "limit": "1",
            },
        )
        if not users:
            created_users = supabase.insert(
                "users",
                {
                    "auth0_sub": current_user.sub,
                    "email": current_user.email or f"{current_user.sub}@local.invalid",
                    "full_name": current_user.name,
                },
                select="id",
            )
            user_id = int(created_users[0]["id"])

            created_orgs = supabase.insert(
                "organizations",
                {"name": "Personal Workspace"},
                select="id",
            )
            org_id = int(created_orgs[0]["id"])

            supabase.insert(
                "organization_memberships",
                {
                    "org_id": org_id,
                    "user_id": user_id,
                    "role": Role.ADMIN.value,
                },
                select="id",
            )

            return TenantContext(org_id=org_id, role=Role.ADMIN, user_id=user_id)

        user_id = int(users[0]["id"])
        memberships = supabase.select(
            "organization_memberships",
            {
                "select": "org_id,role,user_id",
                "user_id": f"eq.{user_id}",
                "limit": "1",
            },
        )
        if not memberships:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization membership")

        membership = memberships[0]
        return TenantContext(
            org_id=int(membership["org_id"]),
            role=membership["role"],
            user_id=int(membership["user_id"]),
        )

    user = db.query(User).filter(User.auth0_sub == current_user.sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not provisioned")

    membership = db.query(OrganizationMembership).filter(OrganizationMembership.user_id == user.id).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization membership")

    return TenantContext(org_id=membership.org_id, role=membership.role, user_id=user.id)
