"""Vercel Python Function exposing EventRadar under /api."""

from backend.app.api.main import app

__all__ = ["app"]
