from datetime import datetime

from pydantic import BaseModel, Field,EmailStr,conint
from typing import Optional, Union, List

from sqlalchemy import orm

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm.mode = True

class PostBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner: User

    class Config:
        orm.mode = True


class PostUpdate(PostBase):
    pass

class Like(BaseModel):
    post_id:int
    dir:conint(ge=0,le=1)

class PostLike(BaseModel):
    Post: Post
    likes:int = 0

    class Config:
        orm.mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id:Optional[int] = None