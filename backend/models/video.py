from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from configs.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)

    file_key = Column(String, nullable=False)

    status = Column(String, nullable=False, default="pending")
    
    file_name = Column(String, nullable=True)

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )