from typing import Optional
from pydantic import BaseModel


# schema for Token


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    is_admin: bool
    is_super_user: bool


# token data
class TokenData(BaseModel):
    id: Optional[int]
    is_admin: Optional[bool]


# schema to get Refresh token
class RefreshToken(BaseModel):
    refresh_token: Optional[str]
