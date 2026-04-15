from sqlalchemy.orm import Session

from app.db.session import Base, SessionLocal, engine
from app.models.entities import Organization, OrganizationMembership, Role, User


def run_seed(db: Session) -> None:
    org_a = db.query(Organization).filter(Organization.name == "Alpha Capital").first()
    org_b = db.query(Organization).filter(Organization.name == "Beta Research").first()

    if not org_a:
        org_a = Organization(name="Alpha Capital")
        db.add(org_a)
        db.flush()

    if not org_b:
        org_b = Organization(name="Beta Research")
        db.add(org_b)
        db.flush()

    admin_user = db.query(User).filter(User.auth0_sub == "auth0|seed-admin").first()
    analyst_user = db.query(User).filter(User.auth0_sub == "auth0|seed-analyst").first()

    if not admin_user:
        admin_user = User(auth0_sub="auth0|seed-admin", email="admin@alpha.example", full_name="Seed Admin")
        db.add(admin_user)
        db.flush()

    if not analyst_user:
        analyst_user = User(auth0_sub="auth0|seed-analyst", email="analyst@beta.example", full_name="Seed Analyst")
        db.add(analyst_user)
        db.flush()

    existing_admin_membership = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.org_id == org_a.id, OrganizationMembership.user_id == admin_user.id)
        .first()
    )
    if not existing_admin_membership:
        db.add(OrganizationMembership(org_id=org_a.id, user_id=admin_user.id, role=Role.ADMIN))

    existing_analyst_membership = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.org_id == org_b.id, OrganizationMembership.user_id == analyst_user.id)
        .first()
    )
    if not existing_analyst_membership:
        db.add(OrganizationMembership(org_id=org_b.id, user_id=analyst_user.id, role=Role.ANALYST))

    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_seed(db)
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
