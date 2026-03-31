import bcrypt
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserResponse
import jwt
import os
from dotenv import load_dotenv
import uuid
load_dotenv()
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
from configs.redis import redisClient
from exceptions import DatabaseError,UserLoginFailedError,JWTTokenError

def hash_password(password: str) -> str:
    encoded_password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(encoded_password, salt)
    return hashed_password.decode('utf-8')

def verify_password(entered_password: str, stored_password: str) -> bool:
    encoded_entered = entered_password.encode('utf-8')
    encoded_stored = stored_password.encode('utf-8')
    return bcrypt.checkpw(encoded_entered, encoded_stored)

def create_user(email: str, password: str, db: Session):
    try:
        hashed_password = hash_password(password)
        new_user = User(email=email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        # Could be a duplicate email (unique constraint), treat as 409
        raise DatabaseError("Failed to create user: " + str(e))
    finally:
        db.close()

def authenticate_user(user: User, db: Session):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if not existing_user:
            raise UserLoginFailedError(status_code=404,message="User not found")
        if not verify_password(user.password, existing_user.password):
            raise UserLoginFailedError(status_code=401,message="Invalid password")
        return existing_user
    finally:
        db.close()

def generate_token(user: UserResponse) -> tuple[str, str, str]:
    refresh_jti = str(uuid.uuid4())
    access_token = jwt.encode(
        {
            "user_id": user.id,
            "type": "access",
            "exp": datetime.now() + timedelta(hours=1)
        },
        os.getenv("JWT_SECRET"), algorithm="HS256"
    )
    refresh_token = jwt.encode(
        {
            "user_id": user.id,
            "type": "refresh",
            "jti": refresh_jti,
            "exp": datetime.now() + timedelta(days=7)
        },
        os.getenv("JWT_SECRET"), algorithm="HS256"
    )
    return access_token, refresh_token, refresh_jti

def get_current_user(request: Request) -> int:
    token = request.cookies.get("access_token")
    print(token)
    if not token:
        raise HTTPException(status_code=401,detail="No access token provided")
    try:
        decoded = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="Access token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="Invalid access token")

    if decoded.get("type") != "access":
        raise HTTPException(status_code=401,detail="Invalid token type")
    user_id = decoded.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401,detail="Malformed token")
    return user_id

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise JWTTokenError(status_code=401,message="Token has expired")
    except jwt.InvalidTokenError:
        raise JWTTokenError(status_code=401,message="Invalid token")

def refresh_access_token(refresh_token: str) -> str:
    decoded = decode_token(refresh_token)  

    if decoded.get("type") != "refresh":
        raise JWTTokenError(status_code=401,message="Invalid token type")

    jti = decoded.get("jti")
    user_id = decoded.get("user_id")

    if not redisClient.redis.exists(jti):
        raise JWTTokenError(status_code=401,message="Refresh token has been revoked")

    new_access_token = jwt.encode(
        {
            "user_id": user_id,
            "type": "access",
            "exp": datetime.now() + timedelta(hours=1)
        },
        os.getenv("JWT_SECRET"), algorithm="HS256"
    )
    return new_access_token