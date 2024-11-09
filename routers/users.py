from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Posts,Likes,Comments,Saved,Followers
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta

router=APIRouter(prefix='/users',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class UserBase(BaseModel):
    username:str
    password:str
    email:str
    
@router.post('/create_user',status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase,db:Session=Depends(get_db)):
    db_user=Users(**user.model_dump())
    db.add(db_user)
    db.commit()
    return{'message':'User successfuly created'}

@router.get('/get_user/{user_id}',status_code=status.HTTP_200_OK)
async def get_user(user_id:int,db:Session=Depends(get_db)):
    user=db.query(Users).filter(Users.id==user_id).first()
    posts=list(db.query(Posts).filter(Posts.user_id==user_id))
    following=list(db.query(Followers).filter(Followers.follower_id==user_id))
    followers=list(db.query(Followers).filter(Followers.followed_id==user_id))
    followers_final=[]
    if len(followers)!=0:
        for f in followers:
            userdb=db.query(Users).filter(Users.id==f.follower_id).first()
            new_follower={
                'follower_id':f.follower_id,
                'followed_id':f.followed_id,
                'follower_username':userdb.username
            }
            followers_final.append(new_follower)
    follows_final=[]
    if len(following)!=0:
        for f in following:
            userdb=db.query(Users).filter(Users.id==f.followed_id).first()
            new_follow={
                'follower_id':f.follower_id,
                'followed_id':f.followed_id,
                'followed_username':userdb.username
            }
            follows_final.append(new_follow)
        
    
    user_final={
        'username':user.username,
        'user_id':user.id,
        'posts':posts,
        'followers':followers_final,
        'follows':follows_final,
        'followers_num':len(followers),
        'follows_num':len(following)
    }
    
    return user_final

@router.put('/update_user')
async def update_user(user_id:int,user:UserBase,db:Session=Depends(get_db)):
    user_db=db.query(Users).filter(Users.id==user_id).first()
    user_db.username=user.username
    user_db.password=user.password
    user_db.email=user_db.email
    db.commit()
    return {'message':'User succesfuly updated'}

@router.delete('/delete_user/{user_id}')
async def delete_user(user_id:int,db:Session=Depends(get_db)):
    user_db=db.query(Users).filter(Users.id==user_id).first()
    db.delete(user_db)
    db.commit()
    return {'message':'User succesfuly deleted'}

@router.get('/search')
async def search(query:str,db:Session=Depends(get_db)):
    results=list(db.query(Users).filter(Users.username.ilike(f"%{query}%")))
    return results

@router.get('/get_users',status_code=status.HTTP_200_OK)
async def get_users(db:Session=Depends(get_db)):
    users=list(db.query(Users))
    return users

@router.post('/login',status_code=status.HTTP_200_OK)
async def login(user:UserBase,db:Session=Depends(get_db)):
    user_db=db.query(Users).filter(Users.username==user.username,Users.password==user.password).first()
    if user_db:
        return {'message':'Loged','user':user_db}