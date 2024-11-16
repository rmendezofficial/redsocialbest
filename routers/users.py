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
from datetime import datetime,timedelta,timezone
import secrets
from fastapi.responses import JSONResponse

ALGORITHM='HS256'
ACCESS_TOKEN_DURATION=180
SECRET='201d573bd73bd7d1344d3a3bfce1550b69102fd11be3db6d379508b6cccc58ea230b'
crypt = CryptContext(schemes=['bcrypt'])

router=APIRouter(prefix='/users',responses={404:{'message':'No encontrado'}})

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
oauth2=OAuth2PasswordBearer(tokenUrl='login')

crypt=CryptContext(schemes=['bcrypt'])
        
class UserBase(BaseModel):
    username:str
    password:str
    email:str
    
@router.post('/create_user',status_code=status.HTTP_201_CREATED)
async def create_user(user:UserBase,db:Session=Depends(get_db)):
    hashed_password = crypt.hash(user.password)
    user.password = hashed_password
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



@router.get('/search')
async def search(query:str,db:Session=Depends(get_db)):
    results=list(db.query(Users).filter(Users.username.ilike(f"%{query}%")))
    return results

@router.get('/get_users',status_code=status.HTTP_200_OK)
async def get_users(db:Session=Depends(get_db)):
    users=list(db.query(Users))
    return users











def create_csrf_token():
    # Genera un token seguro aleatorio de 32 bytes (256 bits)
    return secrets.token_urlsafe(32)

async def auth_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )
    try:
        # Decodifica el token
        usernamedeco = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get('sub')
        if usernamedeco is None:
            raise exception
        # Busca al usuario en la base de datos
        user_dbdeco=db.query(Users).filter(Users.username==usernamedeco).first()
        if user_dbdeco is None:
            raise exception
        return user_dbdeco
    except JWTError:
        raise exception


# Verifica si el usuario está activo
async def current_user(user: Users = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return user


#@router.post('/login',status_code=status.HTTP_200_OK)
#async def login(user:UserBase,db:Session=Depends(get_db)):
#    user_db=db.query(Users).filter(Users.username==user.username,Users.password==user.password).first()
#    if user_db:
#        return {'message':'Loged','user':user_db}
#    return {'message':'An error has ocurred'}

@router.post('/login')
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_db = db.query(Users).filter(Users.username == form.username).first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect user'
        )
    if not crypt.verify(form.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password'
        )
    
    # Genera el token con expiración
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)  # Usando timezone.utc
    access_token = {
        'sub': user_db.username,
        'exp': expiration_time  # Establecer 'exp' en el payload del token
    }
    access_token_final = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    csrf_token_final = create_csrf_token()
    user_info={"username":user_db.username,"email":user_db.email,"id":user_db.id}

    response = JSONResponse(content={"message": "Loged",'access_token': access_token_final, 'token_type': 'bearer','csrf_token':csrf_token_final,'user':user_info})

    user_db.token=csrf_token_final
    db.commit()
    # Establecer la cookie del token CSRF con las configuraciones de seguridad necesarias
    response.set_cookie(
        key="csrf_token",
        value=csrf_token_final,
        httponly=True,       # Permitir acceso desde JavaScript
        samesite="None",
        secure=True# Requiere HTTPS    # Solo permite solicitudes desde el mismo sitio
                                # Tiempo de vida de la cookie en segundos (ej. 30 min)
    )
    
    
    return response

@router.get("/logout")
async def logout(response: JSONResponse):
    # Elimina las cookies del access token y refresh token
    response.delete_cookie("access_token")
    response.delete_cookie("csrf_token")
    
    return {"message": "Logout successful"}


@router.put('/update_user')
async def update_user(request:Request,user_id:int,user:UserBase,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user_db=db.query(Users).filter(Users.id==user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        user_db.username=user.username
        user_db.password=user.password
        user_db.email=user_db.email
        db.commit()
        return {'message':'User succesfuly updated'}
    return {'message':'CSRF FAILED'}

@router.delete('/delete_user/{user_id}')
async def delete_user(request:Request,user_id:int,db:Session=Depends(get_db),user_auth:Users=Depends(current_user)):
    user_db=db.query(Users).filter(Users.id==user_id).first()
    csrf_token_db=user_db.token
    csrf_token_req=request.cookies.get('csrf_token')
    if csrf_token_db==csrf_token_req:
        db.delete(user_db)
        db.commit()
        return {'message':'User succesfuly deleted'}
    return {'message':'CSRF FAILED'}

