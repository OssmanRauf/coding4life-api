from unicodedata import category
from ..schemas import post
from ..core import oauth2
from .. import models
from ..db.database import get_db
from sqlalchemy.orm import Session, contains_eager, joinedload
from fastapi import Depends, status, HTTPException, Response, APIRouter
from typing import List, Optional
from ..schemas.post import PostResponse
import math
from datetime import datetime


# Init router object
router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# URL to GET all posts
@ router.get("/", status_code=status.HTTP_200_OK,
             response_model=PostResponse
             )
def get_all_posts(db: Session = Depends(get_db), search: Optional[str] = "", category: Optional[str] = "", limit: Optional[int] = None, offset: Optional[int] = 0):
    posts_query = db.query(models.Post, models.User).outerjoin(
        models.User).order_by(models.Post.created_at.desc()).filter(models.Post.title.ilike(f"%{search}%"), models.Post.published == True)
    posts_response = posts_query.limit(limit).offset(offset)
    if len(category) > 0:
        posts_response = posts_query.filter(
            models.Post.category == category, models.Post.published == True)
    else:
        posts_response = posts_query.filter(models.Post.published == True)
    # posts = posts_response.all()
    posts_count = posts_query.count()
    num_pages = math.ceil(posts_count/10)

    return {"posts": posts_response.all(), "num_results": posts_count,
            "num_pages": num_pages}


# URL to GET all posts fro one user
@ router.get("/user/{username}", status_code=status.HTTP_200_OK,
             response_model=List[post.PostBase]
             )
def get_posts_from_user(username: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username).first()
    posts = db.query(models.Post).filter(models.Post.owner_id ==
                                         user.id, models.Post.published == True).all()
    # return posts
    return posts


# URL to GET all my posts posts from admin
@ router.get("/user", status_code=status.HTTP_200_OK,
             response_model=List[post.PostBase]
             )
def get_posts_from_admin(db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).filter(
        models.Post.owner_id == current_user.id).all()
    # return posts
    return posts


@ router.get('/categories', status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)):
    print("run")
    categories = db.query(models.Post.category).distinct().all()
    return categories


# URL to POST(Create) a post
@ router.post("/", response_model=post.PostBase,  status_code=status.HTTP_201_CREATED)
def create_post(post: post.PostCreate, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):

    # check if the user is admin
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")
    if not (post.title and post.description and post.content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Someting is missing")
    slug_base = post.title.replace(' ', "-").lower()
    slug = slug_base
    # new_post
    count = 0
    done = False
    while done is False:
        slug_db = db.query(models.Post.slug).filter(
            models.Post.slug == slug).first()
        if not slug_db:
            new_post = models.Post(
                owner_id=current_user.id, slug=slug, **post.dict())
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            done = True
            pass
        else:
            slug = slug_base + "-" + str(count)
            count = int(count)+1
            # return
    return new_post


# GET post by ID
@ router.get("/{id}", status_code=status.HTTP_200_OK, response_model=post.Post)
def get_single_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post, models.User).outerjoin(
        models.User).filter(models.Post.id == id).first()
    # Check if id exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")

    return post


# DELETE post by ID
@ router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    # Check if id exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    # check if the user is admin and if the owner of the post
    if not current_user.is_admin and post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")
    # delete post
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# UPDATE post by id
@ router.put("/{id}", status_code=status.HTTP_201_CREATED)
def update_post(update_post: post.PostCreate, id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    # Check if id exists
    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    # check if the user is admin and if the owner of the post
    if not current_user.is_admin and post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User not authorized to proceed")
    # update post
    # new_post = {owner_id=current_user.id, slug=slug, **post.dict())}
    # new_post = {"owner_id"}
    update_post.updated_at = datetime.now()
    post_query.update(update_post.dict(), synchronize_session=False)
    # post_query.update(created_at=datetime.now())
    db.commit()
    # post_query.created_at = datetime.now()
    return post_query.first()


# GET post by slug
@ router.get("/slug/{slug}", status_code=status.HTTP_200_OK, response_model=post.Post)
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    post = db.query(models.Post, models.User).outerjoin(
        models.User).filter(models.Post.slug == slug).first()
    # Check if id exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")

    return post
