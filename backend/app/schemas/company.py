from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateCompanyRequest(BaseModel):
    name: str


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    owner_id: UUID
    created_at: datetime
