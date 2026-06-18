from pydantic import BaseModel
from typing import Optional


class FeatureFlagCreate(BaseModel):
    name: str
    enabled: bool = False


class FeatureFlagUpdate(BaseModel):
    enabled: bool


class FeatureFlagResponse(BaseModel):
    name: str
    enabled: bool

    model_config = {"from_attributes": True}
