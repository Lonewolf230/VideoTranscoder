import bcrypt
from sqlalchemy.orm import Session
from models.user import User

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
        if existing_user and verify_password(user.password,existing_user.password):
            return existing_user
        else:
            return None
    except Exception as e:
        print("Error authenticating user:", e)
        raise

    finally:
        db.close()
        
