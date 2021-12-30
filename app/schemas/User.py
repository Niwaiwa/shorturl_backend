from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserPassword(BaseModel):
    password: str
    password2: str

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class UserRegister(UserPassword):
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdateLastLogin(BaseModel):
    last_login: datetime


class UserUpdate(BaseModel):
    name: str

