from fastapi import HTTPException,status,APIRouter,Depends
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import database,schemas,models,utils
from .. import oauth
from typing import Annotated

router = APIRouter(
    tags=['Authentication']
)

@router.post("/login",response_model=schemas.Token)
def login(user_credentials: Annotated[OAuth2PasswordRequestForm,Depends()],db: Session = Depends(database.get_db)):
    user = db.query(models.Users).filter(models.Users.email == user_credentials.username).first()

    if user is None or not utils.verify_password(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid credentials!")

    access_token = oauth.create_access_token({"user_id":user.id})

    return schemas.Token(access_token=access_token,token_type="bearer")