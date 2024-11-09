from fastapi import FastAPI
from database import engine,SessionLocal,Base
from fastapi.middleware.cors import CORSMiddleware
from routers import users,posts,saves,comments,likes,followers

origins = [
    "https://a.rcmendez.com", 
]

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(saves.router)
app.include_router(comments.router)
app.include_router(followers.router)

Base.metadata.create_all(bind=engine)
