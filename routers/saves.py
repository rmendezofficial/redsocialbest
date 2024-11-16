from fastapi import FastAPI,HTTPException,Depends,status, APIRouter,Request
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine,SessionLocal,Base
from sqlalchemy.orm import Session
import os
from database import database_db
from models import Users,Comments,Posts,Likes,Followers,Saved
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt,JWTError
from passlib.context import CryptContext
from datetime import datetime,timedelta
from .users import current_user

router=APIRouter(prefix='/saves',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class SaveBase(BaseModel):
    user_id:int
    post_id:int 
    
@router.post('/create_save',status_code=status.HTTP_201_CREATED)
async def create_save(request:Request,save:SaveBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user=db.query(Users).filter(Users.id==save.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        save_db=Saved(**save.model_dump())
        db.add(save_db)
        db.commit()
        return{'message':'Save successfuly created'}
    return {'message':'CSRF FAILED'}

@router.delete('/delete_save/')
async def delete_save(request:Request,save:SaveBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user=db.query(Users).filter(Users.id==save.user_id).first()
    csrf_token_db=user.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        save_db=db.query(Saved).filter(Saved.user_id==save.user_id,Saved.post_id==save.post_id).first()
        db.delete(save_db)
        db.commit()
        return {'message':'Save succesfuly deleted'}
    return {'message':'CSRF FAILED'}



