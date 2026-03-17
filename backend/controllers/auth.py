from schemas.user import UserCreate
from utils.auth import create_user,authenticate_user
from sqlalchemy.orm import Session

def signup(user:UserCreate,db:Session):
    
    try:
        email=user.email
        password=user.password
        
        create_user(email=email,password=password,db=db)
        print("User signed up successfully!")
        
    except Exception as e:
        print("Error signing up user:", e)
        raise
    
def login(user:UserCreate,db:Session):
    
    try:
        return authenticate_user(user=user,db=db)
    except Exception as e:
        print("Error logging in user:", e)
        raise
    
    