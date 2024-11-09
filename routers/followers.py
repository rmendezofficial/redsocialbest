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

router=APIRouter(prefix='/followers',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class FollowBase(BaseModel):
    follower_id:int
    followed_id:int 
    
@router.post('/create_follow',status_code=status.HTTP_201_CREATED)
async def create_follow(follow:FollowBase,db:Session=Depends(get_db)):
    db_follow=Followers(**follow.model_dump())
    db.add(db_follow)
    db.commit()
    return{'message':'Follow successfuly created'}

@router.delete('/delete_follow/')
async def delete_follow(follow:FollowBase,db:Session=Depends(get_db)):
    db_follow=db.query(Followers).filter(Followers.follower_id==follow.follower_id,Followers.followed_id==follow.followed_id).first()
    db.delete(db_follow)
    db.commit()
    return {'message':'Follow succesfuly deleted'}