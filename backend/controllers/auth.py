from schemas.user import UserCreate, UserResponse
from utils.auth import create_user, authenticate_user
from sqlalchemy.orm import Session

def signup(user: UserCreate, db: Session):
    create_user(email=user.email, password=user.password, db=db)

def login(user: UserCreate, db: Session):
    return authenticate_user(user, db)