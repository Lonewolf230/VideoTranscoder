from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.upload import upload_router
app=FastAPI()

origins=[
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def entry_point():
    return {"message": "Welcome to the Video Transcoding API!"}

@app.get("/generate-dummy-data")
def generate_dummy_data():
    return {"message": "Dummy data generated!"}

app.include_router(upload_router)