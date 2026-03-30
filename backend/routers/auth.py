from fastapi import APIRouter, HTTPException, Depends, Response, Request
from schemas.user import UserCreate, UserResponse
from controllers.auth import signup, login
from configs.database import get_db
from utils.auth import generate_token, get_current_user, decode_token, refresh_access_token
from configs.redis import redisClient
from exceptions import DatabaseError, UserLoginFailedError, JWTTokenError,RedisError

auth_router = APIRouter()

@auth_router.post("/signup")
def signup_endpoint(user: UserCreate, db=Depends(get_db)):
    try:
        signup(user, db)
        return {"message": "User signed up successfully!"}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Failed to create user: " + str(e))

@auth_router.post("/login", response_model=UserResponse)
def login_endpoint(user: UserCreate, response: Response, db=Depends(get_db)):
    try:
        authenticated_user = login(user, db)
        access_token, refresh_token, refresh_jti = generate_token(authenticated_user)

        response.set_cookie(key="access_token", value=access_token,
                            httponly=True, samesite="lax", secure=False, max_age=3600)
        response.set_cookie(key="refresh_token", value=refresh_token,
                            httponly=True, samesite="lax", secure=False, max_age=7*24*3600)

        redisClient.set_value(refresh_jti, "valid", ex=7*24*3600)
        return authenticated_user
    except RedisError as e:
        raise HTTPException(status_code=500, detail="Failed to store refresh token in Redis: " + str(e))
    except UserLoginFailedError as e:
        raise HTTPException(status_code=e.status_code,detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail="Login failed")

@auth_router.get("/auth_test")
def auth_test(id=Depends(get_current_user)):
    return {"message": f"Authenticated user ID: {id}"}

@auth_router.post("/logout")
def logout_endpoint(request: Request, response: Response):
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=400, detail="No refresh token provided")

        payload = decode_token(refresh_token)

        try:
            redisClient.delete_value(payload.get("jti"))
        except RedisError as e:
            raise HTTPException(status_code=500, detail="Failed to delete refresh token from Redis: " + str(e))

        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
    except JWTTokenError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Logout failed: " + str(e))

@auth_router.post("/refresh")
def refresh_token_endpoint(request: Request, response: Response):
    try:
        
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token provided")

        new_access_token = refresh_access_token(refresh_token)
        response.set_cookie(key="access_token", value=new_access_token,
                            httponly=True, samesite="lax", secure=False, max_age=3600)
        return {"message": "Access token refreshed successfully!"}
    except JWTTokenError as e:
        return HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to refresh access token: " + str(e))

@auth_router.get("/me")
def get_me(id=Depends(get_current_user)):
    return {"id": id}
