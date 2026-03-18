from fastapi import APIRouter,HTTPException,Depends,Response
from schemas.user import UserCreate,UserResponse
from controllers.auth import signup,login
from configs.database import get_db
from utils.auth import generate_token,get_current_user


auth_router = APIRouter()

@auth_router.post("/signup")
def signup_endpoint(user:UserCreate,db=Depends(get_db)):
    
    try:
        signup(user,db)
        return {"message": "User signed up successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/login",response_model=UserResponse)
def login_endpoint(user:UserCreate,response:Response,db=Depends(get_db)):
    
    try:
        user=login(user,db)
        token=generate_token(user)
        
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=3600
        )
        
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@auth_router.get("/auth_test")
def auth_test(id=Depends(get_current_user)):
    try:
        return {"message": f"Authenticated user ID: {id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    

