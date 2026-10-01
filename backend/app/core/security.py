"""Minimal API key auth dependency. Replace with Azure AD / OAuth2 in
production (see docs/ROADMAP.md, Phase 2)."""

from fastapi import Header, HTTPException

from app.config import get_settings

settings = get_settings()


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != settings.service_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
