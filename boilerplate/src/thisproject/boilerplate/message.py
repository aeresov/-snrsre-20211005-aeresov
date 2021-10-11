from typing import Optional
import pydantic
import datetime


class Message(pydantic.BaseModel):
    url: pydantic.HttpUrl
    status: pydantic.conint(strict=True, ge=100, le=599)
    response_time: datetime.timedelta
    match: Optional[str] = None
