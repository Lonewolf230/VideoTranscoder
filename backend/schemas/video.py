from pydantic import BaseModel

class VideoCreate(BaseModel):
    file_key: str
    file_name : str = None
    
class VideoResponse(BaseModel):
    id: int
    file_key: str
    status: str
    created_at: str
    file_name: str 
    # class Config:
    #     orm_mode = True