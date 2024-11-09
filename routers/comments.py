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

router=APIRouter(prefix='/comments',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class CommentBase(BaseModel):
    user_id:int
    post_id:int
    comment:str
    
@router.post('/create_comment',status_code=status.HTTP_201_CREATED)
async def create_comment(comment:CommentBase,db:Session=Depends(get_db)):
    db_comment=Comments(**comment.model_dump())
    db.add(db_comment)
    db.commit()
    return{'message':'Comment successfuly created'}

@router.put('/update_comment',status_code=status.HTTP_200_OK)
async def update_comment(comment_id:int,comment:CommentBase,db:Session=Depends(get_db)):
    comment_db=db.query(Comments).filter(Comments.id==comment_id).first()
    comment_db.comment=comment.comment
    comment_db.edited=True
    db.commit()
    return {'message':'Comment succesfuly updated'}

@router.delete('/delete_user/{comment_id}')
async def delete_comment(comment_id:int,db:Session=Depends(get_db)):
    comment_db=db.query(Comments).filter(Comments.id==comment_id).first()
    db.delete(comment_db)
    db.commit()
    return {'message':'Comment succesfuly deleted'}