from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    id: int
    username: str
    email: str


class UserCreate(UserBase):
    password: str = Field(alias="password")


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[str]


class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

