from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Comments,Posts,Likes,Followers
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta

router=APIRouter(prefix='/likes',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class LikeBase(BaseModel):
    user_id:int
    post_id:int 
    
@router.post('/create_like',status_code=status.HTTP_201_CREATED)
async def create_like(like:LikeBase,db:Session=Depends(get_db)):
    like_db=Likes(**like.model_dump())
    db.add(like_db)
    db.commit()
    return{'message':'Like successfuly created'}

@router.delete('/delete_like/')
async def delete_like(like:LikeBase,db:Session=Depends(get_db)):
    like_db=db.query(Likes).filter(Likes.user_id==like.user_id,Likes.post_id==like.post_id).first()
    db.delete(like_db)
    db.commit()
    return {'message':'Like succesfuly deleted'}