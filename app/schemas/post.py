from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .user import UserOut
from .comment import Comment


# Base post schema
class PostBase(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool]
    id: Optional[int]
    owner_id: Optional[int]
    category: Optional[str]
    slug: Optional[str]
    description: Optional[str]
    updated_at: Optional[datetime]
    created_at: Optional[datetime]
    header_img: Optional[str]

    class Config:
        orm_mode = True


# Schema for post creation
class PostCreate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool] = False
    category: Optional[str]
    description: Optional[str]
    updated_at: Optional[datetime]
    header_img: Optional[str]

    class Config:
        orm_mode = True


# Schema for response
class Post(BaseModel):
    Post: PostBase
    User: Optional[UserOut]

    class Config:
        orm_mode = True

# class PostResponse(BaseModel):


class PostResponse(BaseModel):
    posts: List[Post]
    num_results: int
    num_pages: int
# Schema for response out


class PostOut(PostBase):
    User: UserOut

    class Config:
        orm_mode = True
