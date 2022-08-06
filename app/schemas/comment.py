from sqlite3 import Date
from pydantic import BaseModel, EmailStr
from datetime import datetime
# from
from .user import UserOut


# Base post schema
class Comment(BaseModel):
    content: str

    class Config:
        orm_mode = True


class CommentIn(Comment):
    id: int
    commented_at: datetime
    email: EmailStr
    username: str


class CommentOut(BaseModel):
    Comment: CommentIn
    User: UserOut

    class Config:
        orm_mode = True


class CommentCreate(Comment):
    post_id: int
