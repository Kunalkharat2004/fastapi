from fastapi import HTTPException,status,Response,Depends,APIRouter
from sqlalchemy.orm import Session
from ..models import Post,Users,Likes
from typing import List
from ..database import get_db
from .. import schemas,oauth
from typing import Annotated
from sqlalchemy import func
from sqlalchemy.sql import label


router = APIRouter(
    prefix="/post",
    tags=['Posts']
)

# Get all post
@router.get("/",response_model=List[schemas.PostLike])
def get_all_post(current_user: Annotated[Users,Depends(oauth.get_current_user)],db: Session = Depends(get_db),limit:int = 10,skip:int = 0,search:str = ""):

    posts = db.query(
        Post,
        label('likes', func.count(Likes.post_id))
    ).outerjoin(
        Likes, Post.id == Likes.post_id
    ).group_by(
        Post.id
    ).filter(Post.title.contains(search)).limit(limit).offset(skip).all()

    print(posts)    #List of objects
    return posts


# Create a New Post
@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post: schemas.PostCreate,current_user: Annotated[Users,Depends(oauth.get_current_user)],db: Session = Depends(get_db)):
    print(type(current_user))
    print(current_user.email)
    new_post = Post(owner_id=current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# Get the latest Post
@router.get("/latest",response_model=schemas.PostLike)
def latest_post(current_user: Annotated[Users,Depends(oauth.get_current_user)],db: Session = Depends(get_db)):
   latest_post = db.query(
        Post,
        label('likes', func.count(Likes.post_id))
    ).outerjoin(
        Likes, Post.id == Likes.post_id
    ).group_by(
        Post.id
    ).order_by(Post.created_at.desc()).first()

   if latest_post is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No post found.")
   return latest_post


# Get a particulat post
@router.get("/{id}",response_model=schemas.PostLike)
def get_post(id:int,current_user: Annotated[Users,Depends(oauth.get_current_user)],db: Session = Depends(get_db)):
    post = db.query(
        Post,
        label('likes', func.count(Likes.post_id))
    ).outerjoin(
        Likes, Post.id == Likes.post_id
    ).group_by(
        Post.id
    ).filter(Post.id == id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {id} doesn't exists.")
    return post


# Delete a post
@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,current_user: Annotated[Users,Depends(oauth.get_current_user)],db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exists.")

    if not post.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not have permission to do that.")


    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update a post
@router.put("/{id}",response_model=schemas.Post)
def update_post(id:int,current_user: Annotated[Users,Depends(oauth.get_current_user)],post: schemas.PostUpdate ,db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == id).first()

    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {id} doesn't exists.")


    if not db_post.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not have permission to do that.")

    post_data = post.dict(exclude_unset = True)

    for key,value in post_data.items():
        setattr(db_post,key,value)
    db.commit()
    db.refresh(db_post)
    return db_post