from ..schemas.comment import CommentOut, CommentCreate
from ..core import oauth2
from .. import models
from ..db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, status, HTTPException, Response, APIRouter
from typing import List

# create router object
router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


# URL to GET all comments
@ router.get("/{slug}", status_code=status.HTTP_200_OK,
             response_model=List[CommentOut]
             )
def get_all_post_comments(slug: str, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.slug == slug).first()
    comment = db.query(models.Comment, models.User).filter(
        models.Comment.post_id == post.id).outerjoin(models.User).order_by(
        models.Comment.commented_at.desc()).all()

    return comment


# DELETE comment by ID
@ router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.id == id)
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    comment = comment_query.first()

    # Check if id exists
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")

    # Check if user is owner of the comment
    if comment.email != user.email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")

# delete comment
    comment_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# create a comment
@ router.post("/",
              response_model=CommentOut,
              status_code=status.HTTP_201_CREATED)
def create_comment_loged_in(comment: CommentCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(
        models.Post.id == comment.post_id).first()
    # check if post exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {comment.post_id} not found")

    # create new_comment
    new_comment = models.Comment(
        email=current_user.email, username=current_user.username, owner_id=current_user.id, **comment.dict())
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    user = db.query(models.User).filter(
        models.User.id == current_user.id).first()
    return {"Comment": new_comment, "User": user}
