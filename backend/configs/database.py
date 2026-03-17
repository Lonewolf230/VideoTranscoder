from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

USER=os.getenv("user")
PASSWORD=os.getenv("password")
HOST=os.getenv("host")
PORT=os.getenv("port")
DBNAME=os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"


engine=create_engine(DATABASE_URL)

Session=sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base=declarative_base()

def get_db():
    db=Session()
    try:
        yield db
    finally:
        db.close()

