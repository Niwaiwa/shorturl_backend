from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, AnyHttpUrl


class KeyDelete(BaseModel):
    key: str
