from fastapi import Depends, status, APIRouter, HTTPException
from schemas.user import AdminRequests
from schemas.user import RequestAnswer, AdminRequests
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
import models
from core import oauth2
from core.utils import conf
from fastapi_mail import MessageSchema, FastMail

# create router object
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# get all requests for admin
@router.get("/requests_for_admin", status_code=status.HTTP_200_OK,
            response_model=List[AdminRequests]
            )
def get_asked_requests(
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    # check if user is super user
    if not current_user.is_super_user:
        print("JJJJJ")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")
    # get all requests for admin and return them
    requests = db.query(models.AdminRequest, models.User).outerjoin(
        models.User).order_by(models.AdminRequest.requested_at.desc()).all()
    # print(requests.user)
    return requests


# Give response to requests
@router.post("/accept_request", status_code=status.HTTP_202_ACCEPTED)
async def accept_request(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)
                         ):
    request = db.query(models.AdminRequest).filter(
        models.AdminRequest.id == id)
    if not request.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
    # check if user is super user
    if not current_user.is_super_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")
    user = db.query(models.User).filter(
        models.User.id == request.first().user_id)
    user.update({"is_admin": True})

    # send email confirmation
    # creating the message to be sent to the email
    message = MessageSchema(
        subject="Response for request to become admin",
        # List of recipients, as many as you can pass
        recipients=[str(user.first().email)],
        template_body={"user": user.first().name},
    )
    # create instance of fastmail
    fm = FastMail(conf)
    # send email confirmming the request for admin
    try:
        await fm.send_message(message, template_name="accepted.html")
    except Exception as e:
        print(e)
    # delete request
    request.delete(synchronize_session=False)
    db.commit()
    return {"message": "User is successfully a new admin"}


# Give response to requests
@router.post("/deny_request", status_code=status.HTTP_202_ACCEPTED)
async def deny_request(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    print("id")
    request = db.query(models.AdminRequest).filter(
        models.AdminRequest.id == id)
    print("request.first()")
    if not request.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # check if user is super user
    if not current_user.is_super_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")
    print("almost deleted")
    user = db.query(models.User).filter(
        models.User.id == request.first().user_id)

    # send email confirmation
    # creating the message to be sent to the email
    message = MessageSchema(
        subject="Response for request to become admin",
        # List of recipients, as many as you can pass
        recipients=[str(user.first().email)],
        template_body={"user": user.first().name},
    )
    # create instance of fastmail
    fm = FastMail(conf)
    # send email confirmming the request for admin
    await fm.send_message(message, template_name="denied.html")
    # delete request
    request.delete(synchronize_session=False)
    db.commit()
    return {"message": "User denied admin habilty"}
