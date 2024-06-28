from fastapi import HTTPException,status,Depends,APIRouter
from sqlalchemy.orm import Session, joinedload
from ..models import Users
from typing import List
from ..database import get_db
from .. import schemas
from ..utils import hash

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# Get all users
@router.get("/",response_model=List[schemas.User])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(Users).all()
    return users


# Get a user by id
@router.get("/{id}",response_model=schemas.User)
def get_user_by_id(id:int,db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id {id} doesn't exists.")

    return user


# Create user
@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.User)
def create_user(user: schemas.UserCreate,db: Session = Depends(get_db)):
    check_user = db.query(Users).filter(Users.email == user.email).first()

    if check_user:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail=f"User with email {user.email} already exists.")

    user.password = hash(user.password)
    new_user = Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
