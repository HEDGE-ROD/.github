"""Minimal fixture mirroring the real hedge-rod-backend RiskScore schema,
used by scripts/self_test_schema_sync.py to verify check_schema_sync.py
reports OK when the two definitions actually agree.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class RiskScore(BaseModel):
    wallet: str
    asset_pair: str
    score: int = Field(ge=0, le=100)
    benford_flag: bool
    ml_flag: bool
    confidence: int = Field(ge=0, le=100)
    timestamp: datetime
