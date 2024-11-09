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
import random

router=APIRouter(prefix='/posts',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class PostBase(BaseModel):
    name:str
    description:str
    user_id:int
    photo:str

@router.post('/create_post',status_code=status.HTTP_201_CREATED)
async def create_post(post:PostBase,db:Session=Depends(get_db)):
    db_post=Posts(**post.model_dump())
    db.add(db_post)
    db.commit()
    return{'message':'Post successfuly created'}

@router.get('/get_post/{post_id}',status_code=status.HTTP_200_OK)
async def get_post(post_id:int,db:Session=Depends(get_db)):
    post_db=db.query(Posts).filter(Posts.id==post_id).first()
    user=db.query(Users).filter(Users.id==post_db.user_id).first()
    comments=list(db.query(Comments).filter(Comments.post_id==post_db.id))
    likes=list(db.query(Likes).filter(Likes.post_id==post_db.id))
    likes_num=len(likes)
    
    comments_final=[]
    for c in comments:
        user=db.query(Users).filter(Users.id==c.user_id).first()
        new_comment={'comment':c.comment,'id':c.id,'user_id':c.user_id,'username':user.username}
        comments_final.append(new_comment)
    post_req={
        'name':post_db.name,
        'description':post_db.description,
        'photo':post_db.photo,
        'user_id':post_db.user_id,
        'username':user.username,
        'comments':comments_final,
        'comments_num':len(comments),
        'likes':likes_num,
        'likes_db':likes
    }
    return post_req

@router.get('/get_posts/',status_code=status.HTTP_200_OK)
async def get_posts(db:Session=Depends(get_db)):
    posts=list(db.query(Posts))
    if posts:
        random.shuffle(posts)
        posts_final=[]
        for p in posts:
            user=db.query(Users).filter(Users.id==p.user_id).first()
            new_post={
                'name': p.name,
                'description': p.description,
                'photo': p.photo,
                'username': user.username,
                'user_id': user.id,
                'id': p.id
            }
            posts_final.append(new_post)
            
        return posts_final
    return {'message':'No posts'}

@router.delete('/delete_post/{post_id}')
async def delete_post(post_id:int,db:Session=Depends(get_db)):
    post_db=db.query(Posts).filter(Posts.id==post_id).first()
    db.delete(post_db)
    db.commit()
    return {'message':'Post succesfuly deleted'}
