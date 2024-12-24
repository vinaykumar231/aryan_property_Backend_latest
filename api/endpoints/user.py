from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException,Form
from sqlalchemy.orm import Session
from auth.auth_bearer import JWTBearer, get_admin, get_current_user
from database import get_db, api_response
from ..models.user import AriyanspropertiesUser
from ..schemas import LoginInput, ChangePassword, UserCreate, UpdateUser, UserType
import bcrypt
import random
import pytz


router = APIRouter()

user_ops = AriyanspropertiesUser()


def generate_token(data):
    exp = datetime.utcnow() + timedelta(days=1)
    token_payload = {'user_id': data['emp_id'], 'exp': exp}
    token = jwt.encode(token_payload, 'cat_walking_on_the street', algorithm='HS256')
    return token, exp


@router.post('/AriyanspropertiesUsers/login/')
async def AriyanspropertiesUsers(credential: LoginInput):
    try:
        response = user_ops.AriyanspropertiesUsers_login(credential)
        return response
    except HTTPException as e:
        raise
    except Exception as e:
        return HTTPException(status_code=500, detail=f"login failed: {str(e)}")


@router.post("/insert/AriyanspropertiesUser_register/")
def AriyanspropertiesUser_register(data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not AriyanspropertiesUser.validate_email(data.user_email):
            raise HTTPException(status_code=400, detail="Invalid email format")

        if not AriyanspropertiesUser.validate_password(data.user_password):
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

        if not AriyanspropertiesUser.validate_phone_number(data.phone_no):
            raise HTTPException(status_code=400, detail="phone number must be 10 digit")

        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        # hashed_password = bcrypt.hashpw(data.user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        usr = AriyanspropertiesUser(
            user_name=data.user_name,
            user_email=data.user_email,
            user_password=data.user_password,
            user_type=data.user_type, 
            phone_no=data.phone_no,
            created_on=ist_now,
            updated_on=ist_now
        )
        db.add(usr)
        db.commit()

        response = api_response(200, message="User Created successfully")
        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=f"{e}")
    
@router.put("/update_user_type/", response_model=None, dependencies=[Depends(JWTBearer()), Depends(get_admin)])
async def update_user_type(user_id: int, user_type: str, db: Session = Depends(get_db)):
    try:
        user_db = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_db.user_type = user_type
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        return {"message": "User type updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.get("/get_my_profile")
def get_current_user_details(current_user: AriyanspropertiesUser = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user_details = {
            # "user_id": current_user.user_id,
            "username": current_user.user_name,
            "email": current_user.user_email,
            "user_type": current_user.user_type,
            "phone_no" : current_user.phone_no,

        }
        return api_response(data=user_details, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")



