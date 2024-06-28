from fastapi import APIRouter,status,HTTPException,Depends
from .. import database,models,schemas,oauth
from sqlalchemy.orm import Session
from typing import Annotated

router = APIRouter(
    prefix="/like",
    tags=["Likes"]
)

@router.post("/",status_code=status.HTTP_200_OK)
def like(like: schemas.Like,current_user: models.Users = Depends(oauth.get_current_user),db: Session = Depends(database.get_db)):

    post = db.query(models.Post).filter(models.Post.id == like.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Post with id {like.post_id} doesn't exists.")

    found_post = db.query(models.Likes).filter(models.Likes.post_id == like.post_id, models.Likes.user_id == current_user.id).first()

    if like.dir == 1:
        if found_post:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"You already liked the post with id {like.post_id}")

        liked_post = models.Likes(post_id=like.post_id,user_id=current_user.id)
        db.add(liked_post)
        db.commit()
        return {"message":"Successfully liked the post"}

    else:
        if not found_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"You have already disliked the post")

        db.delete(found_post)
        db.commit()
        return {"message":f"Successfully disliked post with id {like.post_id}"}
