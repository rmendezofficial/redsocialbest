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
from .users import current_user

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
async def create_follow(request:Request,follow:FollowBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user=db.query(Users).filter(Users.id==follow.follower_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db_follow=Followers(**follow.model_dump())
        db.add(db_follow)
        db.commit()
        return{'message':'Follow successfuly created'}
    return {'message':'CSRF FAILED'}

@router.delete('/delete_follow/')
async def delete_follow(request:Request,follow:FollowBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user=db.query(Users).filter(Users.id==follow.follower_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db_follow=db.query(Followers).filter(Followers.follower_id==follow.follower_id,Followers.followed_id==follow.followed_id).first()
        db.delete(db_follow)
        db.commit()
        return {'message':'Follow succesfuly deleted'}
    return {'message':'CSRF FAILED'}

