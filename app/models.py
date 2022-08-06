from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from .db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, false
from sqlalchemy.orm import relationship


# Post Model(Table)
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    content = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    published = Column(Boolean, default=False)
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("NOW()"))
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("NOW()"))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="post")
    comments = relationship("Comment", backref="post")
    category = Column(String, nullable=True)


# Comment Model(Table)
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=True)
    username = Column(String, nullable=True)
    content = Column(String, nullable=False)
    commented_at = Column(TIMESTAMP(timezone=True),
                          nullable=False, server_default=text("NOW()"))
    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    # post = relationship("Post", back_populates="comments")


# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("NOW()"))
    description = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, server_default=text("False"))
    is_super_user = Column(Boolean, default=False,
                           server_default=text("False"))
    profile_url = Column(String, nullable=True)


class AdminRequest(Base):
    __tablename__ = "adminrequests"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    requested_at = Column(TIMESTAMP(timezone=True),
                          nullable=False, server_default=text("NOW()"))
