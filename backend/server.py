from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.upload import upload_router
from configs.database import Base,engine
from configs.sqs import SQSClient
app=FastAPI()

origins=[
    "http://localhost:5173",
]

#not the ideal way but for now we can create tables like this, later we can use alembic for migrations
Base.metadata.create_all(bind=engine)

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

# @app.post("/send-test-message")
# def send_test_message():
#     sqs.send_message("Hello da punda mavane")
#     return {"message": "Message sent to SQS!"}

# @app.get("/receive-messages")
# def receive_messages():
#     messages=sqs.receive_messages()
#     return {"messages": messages}

# @app.delete("/delete-message")
# def delete_message(receipt_handle:str):
#     sqs.delete_message(receipt_handle)
#     return {"message": "Message deleted from SQS!"}

app.include_router(upload_router)