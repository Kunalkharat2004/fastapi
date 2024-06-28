import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime,timedelta,timezone
from typing import Annotated
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
from .schemas import TokenData
from . import database,models
from sqlalchemy.orm import Session
from .config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        print(f"this is the token: {token}")
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
        print(token_data)

    except InvalidTokenError:
        raise credentials_exception

    user = db.query(models.Users).filter(models.Users.id == id).first()
    if user is None:
        raise credentials_exception

    return user
