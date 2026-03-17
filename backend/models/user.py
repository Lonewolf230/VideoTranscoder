from sqlalchemy import Column,Integer,String,TIMESTAMP,func
from configs.database import Base

class User(Base):
    
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    
    email=Column(String,unique=True,nullable=False)
    
    password=Column(String,nullable=False)
    
    created_at=Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.now()
    )