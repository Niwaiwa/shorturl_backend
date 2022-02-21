from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, AnyHttpUrl


class UrlCreate(BaseModel):
    origin_url: AnyHttpUrl
    key: Optional[str] = None

class UrlDelete(BaseModel):
    key: str

class UrlGet(BaseModel):
    page: int
    count: int