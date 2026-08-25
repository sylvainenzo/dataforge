import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CertificateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    course_id: uuid.UUID | None
    learning_path_id: uuid.UUID | None
    title: str
    certificate_number: str
    issued_at: datetime


class CertificateVerification(BaseModel):
    certificate_number: str
    recipient_name: str
    course_title: str
    issued_at: datetime
