from fastapi import APIRouter,HTTPException,Depends
from schemas.user import UserCreate,UserResponse
from controllers.auth import signup,login
from configs.database import get_db



auth_router = APIRouter()

@auth_router.post("/signup")
def signup_endpoint(user:UserCreate,db=Depends(get_db)):
    
    try:
        signup(user,db)
        return {"message": "User signed up successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/login",response_model=UserResponse)
def login_endpoint(user:UserCreate,db=Depends(get_db)):
    
    try:
        return login(user,db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

