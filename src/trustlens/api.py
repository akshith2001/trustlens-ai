"""Authenticated HTTP interface for TrustLens governance decisions."""

from __future__ import annotations

import hmac
import os
from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from trustlens import __version__
from trustlens.governance import determine_governance_action
from trustlens.monitoring import GovernanceMonitor
from trustlens.registry import FileRegistry


class GovernanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    probability: float = Field(ge=0, le=1)
    drift_auc: float = Field(default=0.5, ge=0, le=1)
    is_out_of_distribution: bool = False


class GovernanceResponse(BaseModel):
    action: str
    reason: str


def create_app(
    *,
    api_key: str | None = None,
    registry_path: Path | None = None,
    monitor: GovernanceMonitor | None = None,
) -> FastAPI:
    """Create an app with explicit dependencies for testability and deployment."""

    configured_key = api_key or os.getenv("TRUSTLENS_API_KEY")
    registry = FileRegistry(registry_path or Path("artifacts/model_registry.json"))
    runtime_monitor = monitor or GovernanceMonitor()

    def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
        if not configured_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API authentication is not configured",
            )
        if x_api_key is None or not hmac.compare_digest(x_api_key, configured_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid API key",
            )

    app = FastAPI(
        title="TrustLens Governance API",
        version=__version__,
        description="Research-only governance API; never a lending decision service.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.post(
        "/v1/governance/evaluate",
        response_model=GovernanceResponse,
        dependencies=[Depends(require_api_key)],
    )
    def evaluate(request: GovernanceRequest) -> GovernanceResponse:
        action, reason = determine_governance_action(
            request.probability,
            drift_auc=request.drift_auc,
            is_out_of_distribution=request.is_out_of_distribution,
        )
        runtime_monitor.record(
            probability=request.probability,
            drift_auc=request.drift_auc,
            is_ood=request.is_out_of_distribution,
            action=action,
        )
        return GovernanceResponse(action=action, reason=reason)

    @app.get("/v1/monitoring", dependencies=[Depends(require_api_key)])
    def monitoring() -> dict[str, object]:
        return asdict(runtime_monitor.snapshot())

    @app.get("/v1/models", dependencies=[Depends(require_api_key)])
    def models() -> list[dict[str, object]]:
        return [asdict(model) for model in registry.list_models()]

    return app


app = create_app()
