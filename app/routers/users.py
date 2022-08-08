from random import randint
from .. import models
from ..db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter, HTTPException, Response
from typing import List
from ..core import utils
from ..schemas.user import User, UserCreate, UserUpdate
from ..core import oauth2
from fastapi_mail import FastMail, MessageSchema
from ..core.utils import conf
from email_validator import validate_email, EmailNotValidError
from fastapi import File, UploadFile
import shutil
import os
from fastapi.responses import FileResponse
from validate_email import validate_email as py3_validate_email


# create router object
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# URL to GET all users
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[User])
def get_all_users(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users


# URL to POST(Create) a user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    username = db.query(models.User).filter(
        models.User.username == user.username).first()
    user_email = db.query(models.User).filter(
        models.User.email == user.email.lower()).first()

    # check if email is valid
    try:
        is_valid = py3_validate_email(email_address=user.email)
        email = validate_email(user.email)
        if email.domain != "gmail.com":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email must be gmail.com")
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"The email address is not valid")
    except EmailNotValidError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"The email address is not valid")

    # check if username is taken
    if username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Username taken pleasse try again")

    # check if user is my-profile
    if user.username == "my-profile":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"sername taken pleasse try again")

    # check if the email has an account already
    if user_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Another account is using this email")
    # hash password with utils function
    user.password = utils.hash(user.password)
    user.email = user.email.lower()
    # create user
    if user.email == "coding4lifeblog@gmail.com":
        new_user = models.User(
            is_super_user=True, is_admin=True, ** user.dict())
    else:
        new_user = models.User(is_super_user=False,
                               is_admin=False, ** user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/add/profile", status_code=status.HTTP_201_CREATED)
async def add_profile_pic(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_query = db.query(models.User).filter(
        models.User.id == current_user.id)
    if "image" not in file.content_type:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The file must be a image")
    user = user_query.first()
    if user.profile_url and not os.path.exists(path):
        user_query.first().profile_url = None
    if user.profile_url:

        path = os.path.join(os.path.dirname(
            __file__), '..', f'core/profile_pics/{user.profile_url}')
        os.remove(path)
        user_query.first().profile_url = None
        db.commit()

    try:
        random = randint(600, 100000)
        file.filename = str(random)+"_profile_pic.png"
        path = os.path.join(os.path.dirname(
            __file__), '..', f'core/profile_pics/{file.filename}')
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            buffer.close()
    except Exception as e:
        return e
    finally:
        # file.close()
        # user = user_query.dict()
        user_query.first().profile_url = file.filename
        # user_query.update()
        db.commit()
    return {'message': "Picture added succesfully"}


@router.get("/profile_pic/{username}")
def get_profile_pic(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    path = os.path.join(os.path.dirname(
        __file__), '..', f'core/profile_pics/{user.profile_url}')
    base_path = os.path.join(os.path.dirname(
        __file__), '..', 'core/profile_pics/base_image.png')
    if not os.path.isfile(path):
        if not os.path.isfile(base_path):

            # print("kjjj", base_path)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return FileResponse(base_path)
    return FileResponse(path)


@router.put("/delete/profile", status_code=status.HTTP_201_CREATED)
def delete_profile_pic(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_query = db.query(models.User).filter(
        models.User.id == current_user.id)
    user = user_query.first()
    if user.profile_url and not os.path.exists(path):
        user_query.first().profile_url = None
    if not user.profile_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    path = os.path.join(os.path.dirname(
        __file__), '..', f'core/profile_pics/{user.profile_url}')

    os.remove(path)
    user_query.first().profile_url = None
    db.commit()
    return {"message": "User profile removed"}


# Get user by token
@router.get("/myprofile", status_code=status.HTTP_200_OK, response_model=User)
def get_my_user_info(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    # Check if id exists
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found")

    return user


# Get user by username
@router.get("/{username}", status_code=status.HTTP_200_OK, response_model=User)
def get_single_user(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username).first()
    # Check if id exists
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {1} not found")

    return user


# UPDATE user
@ router.put("/{id}", status_code=status.HTTP_201_CREATED, response_model=User)
async def update_user(update_user: UserUpdate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(
        models.User.id == current_user.id)

    try:
        is_valid = py3_validate_email(
            email_address=update_user.email)
        email = validate_email(update_user.email)
        if email.domain != "gmail.com":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Email must be gmail.com")

        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"The email address is not valid")
    except EmailNotValidError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"The email address is not valid")
    user = user_query.first()
    # update_user.password = user_query.first().password
    # update user
    user_query.update(update_user.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()


# DELETE post by ID
@ router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(
        models.User.id == current_user.id)
    user = user_query.first()

    # check if the user is current_user
    if current_user.id != user.id or not current_user.is_super_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Cannot to that")
    # delete post
    user_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# route to make a admin request
@router.post("/request-admin", status_code=status.HTTP_201_CREATED)
async def request_admin_hability(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    request = db.query(models.AdminRequest).filter(
        models.AdminRequest.user_id == current_user.id).first()
    # check if user has email and user registered to its account and name
    if not current_user.email and not current_user.username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Email or username not found, pleasse fill all of your informations and then request again")
    # check if user has a name registered to its account and name
    if current_user.name is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Name not found, pleasse complete your informations and then request again")
    # check if user has a description
    if current_user.name is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pleasse add an bio to yout profile and then request again")
    # check if is already an admin
    if current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User {current_user.username} is already an admin")
    # check if user has already requested for admin
    if request:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"You've already requested for admin wait for the approval")

    # creating the message to be sent to the email
    message = MessageSchema(
        subject="Request to become admin",
        # List of recipients, as many as you can pass
        recipients=[str(current_user.email)],
        template_body={"user": current_user.name},
    )
    # create and save request to database
    user_request = {"user_id": current_user.id}
    new_request = models.AdminRequest(**user_request)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # create instance of fastmail
    fm = FastMail(conf)
    # send email confirmming the request for admin
    try:
        await fm.send_message(message, template_name="index.html")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="something went wrong")
    return {"message": "Request succesful pleasse wait for our email"}
