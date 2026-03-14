from pydantic import BaseModel

class VideoCreate(BaseModel):
    file_key: str
    
class VideoResponse(BaseModel):
    id: int
    file_key: str
    status: str
    created_at: str

    # class Config:
    #     orm_mode = True