from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.upload import upload_router
from routers.auth import auth_router
from routers.post_upload import post_upload_router
from configs.database import Base,engine
app=FastAPI()
import os

origins=[
    os.getenv("FRONTEND_URL","http://localhost:5173")
]

#not the ideal way but for now we can create tables like this, later we can use alembic for migrations
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

@app.get("/")
def entry_point():
    return {"message": "Welcome to the Video Transcoding API!"}

@app.get("/generate-dummy-data")
def generate_dummy_data():
    return {"message": "Dummy data generated!"}


app.include_router(upload_router)
app.include_router(auth_router)
app.include_router(post_upload_router)