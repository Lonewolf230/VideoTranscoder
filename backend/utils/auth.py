import bcrypt
from sqlalchemy.orm import Session
from models.user import User
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import Request
from datetime import datetime,timedelta


def hash_password(password:str)->str:
    
    encoded_password=password.encode('utf-8')
    salt=bcrypt.gensalt() # default 12 rounds
    hashed_password=bcrypt.hashpw(encoded_password,salt)
    return hashed_password.decode('utf-8')

def verify_password(entered_password:str, stored_password:str)->bool:
    
    encoded_entered_password=entered_password.encode('utf-8')
    encoded_stored_password=stored_password.encode('utf-8')
    return bcrypt.checkpw(encoded_entered_password,encoded_stored_password)


def create_user(email:str,password:str,db:Session):
    
    try:
        hashed_password=hash_password(password)
        new_user=User(email=email,password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print("Error creating user:", e)
        raise
    finally:
        db.close()
    
def authenticate_user(user:User,db:Session):
    
    try:
        existing_user=db.query(User).filter(User.email == user.email).first()
        if not existing_user:
            raise Exception("User not found")
        if not verify_password(user.password,existing_user.password):
            raise Exception("Invalid password")
        return existing_user
    except Exception as e:
        print("Error authenticating user:", e)
        raise

    finally:
        db.close()
        
        
def generate_token(user:User)->tuple[str,str]:
    """ Function to generate JWT token for authenticated users. """
    try:
        encoded_jwt_access_token = jwt.encode(
            {
                "user_id":user.id,
                "type":"access",
                "exp": datetime.now(datetime.timezone.utc) + timedelta(hours=1)
            },os.getenv("JWT_SECRET"),algorithm="HS256")
        
        # finish refreshtoken and logout flow
        
        encoded_jwt_refresh_token = jwt.encode(
            {
                "user_id":user.id,
                "type":"refresh",
                "exp": datetime.now(datetime.timezone.utc) + timedelta(days=7)
             },os.getenv("JWT_SECRET"),algorithm="HS256")    
            
        return encoded_jwt_access_token, encoded_jwt_refresh_token
    except Exception as e:
        print("Error generating token:", e)
        raise
    
def get_current_user(request:Request)->int:
    
    try:
        token=request.cookies.get("access_token")
        if not token:
            raise Exception("No access token provided")
        decoded_token=jwt.decode(token,os.getenv("JWT_SECRET"),algorithms=["HS256"])
        user_id=decoded_token.get("user_id")
        print(f"Decoded token: {decoded_token}")
        if not user_id:
            raise Exception("Invalid token")
        return user_id
    except Exception as e:
        print("Error getting current user:", e)
        raise
