from pydantic import BaseModel
from typing import Optional


class TemplateCreate(BaseModel):
    name: str
    subject: str
    body_template: str


class TemplateUpdate(BaseModel):
    subject: Optional[str] = None
    body_template: Optional[str] = None


class TemplateResponse(BaseModel):
    name: str
    subject: str
    body_template: str

    model_config = {"from_attributes": True}
