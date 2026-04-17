from __future__ import annotations

from functools import lru_cache
from typing import Any

import requests
from fastapi import HTTPException, status

from app.core.config import Settings, get_settings


class SupabaseRestClient:
    def __init__(self, settings: Settings) -> None:
        if settings.data_backend != "supabase_rest":
            raise RuntimeError("Supabase REST client used while data_backend is not supabase_rest")
        if not settings.supabase_url:
            raise RuntimeError("SUPABASE_URL is required when DATA_BACKEND=supabase_rest")
        if not settings.supabase_service_role_key:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is required when DATA_BACKEND=supabase_rest")

        self.base_url = settings.supabase_url.rstrip("/") + "/rest/v1"
        self.timeout = settings.external_request_timeout_seconds
        self._headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        table: str,
        *,
        params: dict[str, str] | None = None,
        payload: Any | None = None,
        prefer: str | None = None,
    ) -> Any:
        headers = dict(self._headers)
        if prefer:
            headers["Prefer"] = prefer

        try:
            response = requests.request(
                method=method,
                url=f"{self.base_url}/{table}",
                headers=headers,
                params=params,
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Supabase request failed: {exc}",
            ) from exc

        if response.status_code >= 400:
            detail = response.text.strip() or f"status {response.status_code}"
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Supabase error: {detail}",
            )

        if not response.text:
            return None
        return response.json()

    def select(self, table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
        data = self._request("GET", table, params=params)
        return data if isinstance(data, list) else []

    def insert(
        self,
        table: str,
        payload: dict[str, Any] | list[dict[str, Any]],
        select: str = "*",
    ) -> list[dict[str, Any]]:
        params = {"select": select} if select else None
        data = self._request("POST", table, params=params, payload=payload, prefer="return=representation")
        return data if isinstance(data, list) else []

    def update(
        self,
        table: str,
        payload: dict[str, Any],
        filters: dict[str, str],
        select: str = "*",
    ) -> list[dict[str, Any]]:
        params = dict(filters)
        if select:
            params["select"] = select
        data = self._request("PATCH", table, params=params, payload=payload, prefer="return=representation")
        return data if isinstance(data, list) else []

    def delete(self, table: str, filters: dict[str, str]) -> None:
        self._request("DELETE", table, params=filters)


@lru_cache
def get_supabase_rest_client() -> SupabaseRestClient:
    return SupabaseRestClient(get_settings())
