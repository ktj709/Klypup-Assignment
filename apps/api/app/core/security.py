from typing import Any
import time

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.entities import OrganizationMembership, User
from app.schemas.auth import CurrentUser

security = HTTPBearer(auto_error=False)
_JWKS_CACHE: dict[str, Any] | None = None
_JWKS_CACHE_TS: float = 0.0
_JWKS_CACHE_TTL_SECONDS = 300


def _fetch_jwks() -> dict[str, Any]:
    settings = get_settings()
    if not settings.auth0_domain:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Auth0 domain not configured")
    jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
    global _JWKS_CACHE
    global _JWKS_CACHE_TS

    now = time.time()
    if _JWKS_CACHE and (now - _JWKS_CACHE_TS) < _JWKS_CACHE_TTL_SECONDS:
        return _JWKS_CACHE

    retries = max(1, settings.external_request_retries + 1)
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.get(jwks_url, timeout=settings.external_request_timeout_seconds)
            response.raise_for_status()
            _JWKS_CACHE = response.json()
            _JWKS_CACHE_TS = time.time()
            return _JWKS_CACHE
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries - 1:
                break
            time.sleep(0.2 * (attempt + 1))

    raise requests.RequestException("Unable to fetch JWKS after retries") from last_error


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> CurrentUser:
    settings = get_settings()

    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials

    if not settings.auth0_domain or not settings.auth0_audience:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Auth0 settings are missing")

    try:
        jwks = _fetch_jwks()
        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to find matching key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.auth0_algorithms],
            audience=settings.auth0_audience,
            issuer=f"https://{settings.auth0_domain}/",
        )

    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to fetch Auth0 keys") from exc

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub")

    user = db.query(User).filter(User.auth0_sub == sub).first()
    if not user:
        user = User(
            auth0_sub=sub,
            email=payload.get("email", "unknown@example.com"),
            full_name=payload.get("name"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    membership = db.query(OrganizationMembership).filter(OrganizationMembership.user_id == user.id).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to an organization",
        )

    return CurrentUser(sub=sub, email=payload.get("email"), name=payload.get("name"))
