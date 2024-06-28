from fastapi import FastAPI
from .models import Base
from .database import engine
from .routes import post,user,auth,like

# Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
def root():
    return {
       "Message":"This is a message from root path"
            }

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(like.router)



# from typing import Annotated
#
# from fastapi import Depends, FastAPI
# from fastapi.security import OAuth2PasswordBearer
#
# app = FastAPI()
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}