from core import oauth2, utils
from schemas import token
import models
from db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


# Init router object
router = APIRouter(
    tags=["Oauth"]
)


# Login Path
@router.post("/login",
             # response_model=token.Token
             )
def login(userCredentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == userCredentials.username).first()

    # check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # check if password entered and the hashed are te same
    if not utils.verify(userCredentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    # create acess and refresh tokens
    access_token = oauth2.create_acess_token(
        data={"user_id": user.id, "is_admin": user.is_admin, "is_super_user": user.is_super_user})
    refresh_token = oauth2.create_refresh_token(
        data={"user_id": user.id})
    # user_dict = user.cop
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",
            "is_admin": user.is_admin,
            "is_super_user": user.is_super_user}


# Refresh token
@router.get("/refresh_token")
def refresh_token(tokens: str = Depends(oauth2.refresh_token)):
    print(tokens)
    return tokens
