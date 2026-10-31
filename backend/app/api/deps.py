"""Shared FastAPI dependencies injected into route handlers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.services.orchestrator import ReviewOrchestrator

# Convenience alias for settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_orchestrator(settings: SettingsDep) -> ReviewOrchestrator:
    """Dependency provider for ReviewOrchestrator."""
    return ReviewOrchestrator(settings=settings)


OrchestratorDep = Annotated[ReviewOrchestrator, Depends(get_orchestrator)]
