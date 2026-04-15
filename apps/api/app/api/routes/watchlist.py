from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.tenant import get_tenant_context
from app.db.session import get_db
from app.models.entities import CompanyWatchlist
from app.schemas.auth import TenantContext
from app.schemas.watchlist import WatchlistCreate, WatchlistOut

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistOut])
def list_watchlist(
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[CompanyWatchlist]:
    return (
        db.query(CompanyWatchlist)
        .filter(CompanyWatchlist.org_id == tenant.org_id)
        .order_by(CompanyWatchlist.created_at.desc())
        .all()
    )


@router.post("", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
def add_watchlist_item(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> CompanyWatchlist:
    ticker = payload.ticker.strip().upper()
    existing = (
        db.query(CompanyWatchlist)
        .filter(CompanyWatchlist.org_id == tenant.org_id, CompanyWatchlist.ticker == ticker)
        .first()
    )
    if existing:
        return existing

    item = CompanyWatchlist(
        org_id=tenant.org_id,
        ticker=ticker,
        company_name=payload.company_name,
        created_by_user_id=tenant.user_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist_item(
    watchlist_id: int,
    db: Session = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> None:
    item = (
        db.query(CompanyWatchlist)
        .filter(CompanyWatchlist.id == watchlist_id, CompanyWatchlist.org_id == tenant.org_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item not found")

    db.delete(item)
    db.commit()
    return None
