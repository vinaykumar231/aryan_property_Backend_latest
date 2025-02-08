from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException,Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.models.logs import Logs
from auth.auth_bearer import JWTBearer, get_admin, get_current_user
from database import get_db, api_response
from ..models.user import AriyanspropertiesUser
from ..schemas import LoginInput, ChangePassword, UserCreate, UpdateUser, UserType
import bcrypt
import random
import pytz
from sqlalchemy.exc import SQLAlchemyError
from enum import Enum


router = APIRouter()

user_ops = AriyanspropertiesUser()


def generate_token(data):
    exp = datetime.utcnow() + timedelta(days=1)
    token_payload = {'user_id': data['emp_id'], 'exp': exp}
    token = jwt.encode(token_payload, 'cat_walking_on_the street', algorithm='HS256')
    return token, exp


@router.post('/AriyanspropertiesUsers/login/')
async def AriyanspropertiesUsers(credential: LoginInput, db: Session = Depends(get_db)):
    try:
        response = user_ops.AriyanspropertiesUsers_login(credential)
        return response
    except HTTPException as e:
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while login.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while login.")


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

        log_action=Logs(
            user_id=usr.user_id,
            action=f"new {usr.user_name} User Created",
            #property_id="None",
            timestamp=ist_now,
        )
        db.add(log_action)
        db.commit()

        response = api_response(200, message="User Created successfully")
        return response
    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while register.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred  while register.")
    
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

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while update user type.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while update user type.")

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
    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while get profile.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while get profile.")
    
@router.get("/get_all_users")
def get_all_users(db: Session = Depends(get_db)):
    try:
        # Query to fetch all user records
        users = db.query(AriyanspropertiesUser).all()
        
        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        # Map user details into a readable format
        user_list = [
            {
                "user_id": user.user_id,
                "username": user.user_name,
                "email": user.user_email,
                "user_type": user.user_type,
                "phone_no": user.phone_no,
            }
            for user in users
        ]

        return api_response(data=user_list, status_code=200)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while get all users.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while get all users.")
    
@router.delete("/delete/AriyanspropertiesUser/{user_id}")
def delete_ariyansproperties_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user_to_delete = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found.")
        
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))

        log_action = Logs(
            user_id=user_id,  
            action=f"Deleted user {user_to_delete.user_name}",
            timestamp=ist_now
        )
        
        db.add(log_action)
        db.commit()

        # Delete the user
        db.delete(user_to_delete)
        db.commit()

        return {"message": "User deleted successfully."}

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while delete user .")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while delete user.")
    
################################################# user permissions all api ###############################################

@router.put("/permissions/can_add/{user_id}", response_model=None)
async def update_can_add_permission(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
        if not user:
           raise HTTPException(status_code=404, detail="User not found.")
        
        user.can_add = True
        db.commit()
        db.refresh(user)

        return {
            "user_id":user.user_id,
            "user_name":user.user_name,
            "user_email":user.user_email,  
            "user_type" :user.user_type,
            "phone_no" :user.phone_no,
            "can_print_report": user.can_print_report,
            "can_add": user.can_add,
            "can_view" :user.can_view,
            "can_edit" :user.can_edit,
            "can_delete": user.can_delete,

        }
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating print report permission.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred whileupdating print report permission.")

 
@router.put("/permissions/can_view/{user_id}", response_model=None)
async def update_can_view_permission(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
        if not user:
           raise HTTPException(status_code=404, detail="User not found.")
        
        user.can_view = True
        db.commit()
        db.refresh(user)

        return {
            "user_id":user.user_id,
            "user_name":user.user_name,
            "user_email":user.user_email,  
            "user_type" :user.user_type,
            "phone_no" :user.phone_no,
            "can_print_report": user.can_print_report,
            "can_add": user.can_add,
            "can_view" :user.can_view,
            "can_edit" :user.can_edit,
            "can_delete": user.can_delete,

        }
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating can view permission.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred whileupdating can view permission.")
    
@router.put("/permissions/can_edit/{user_id}", response_model=None)
async def update_can_edit_permission(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
        if not user:
           raise HTTPException(status_code=404, detail="User not found.")
        
        user.can_edit = True
        db.commit()
        db.refresh(user)

        return {
            "user_id":user.user_id,
            "user_name":user.user_name,
            "user_email":user.user_email,  
            "user_type" :user.user_type,
            "phone_no" :user.phone_no,
            "can_print_report": user.can_print_report,
            "can_add": user.can_add,
            "can_view" :user.can_view,
            "can_edit" :user.can_edit,
            "can_delete": user.can_delete,

        }
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating can edit permission.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred whileupdating can edit permission.")
    
@router.put("/permissions/can_delete/{user_id}", response_model=None)
async def update_can_delete_permission(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
        if not user:
           raise HTTPException(status_code=404, detail="User not found.")
        
        user.can_delete = True
        db.commit()
        db.refresh(user)

        return {
            "user_id":user.user_id,
            "user_name":user.user_name,
            "user_email":user.user_email,  
            "user_type" :user.user_type,
            "phone_no" :user.phone_no,
            "can_print_report": user.can_print_report,
            "can_add": user.can_add,
            "can_view" :user.can_view,
            "can_edit" :user.can_edit,
            "can_delete": user.can_delete,

        }
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating can delete permission.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred whileupdating can delete permission.")
    
@router.put("/permissions/print-report/{user_id}", response_model=None)
async def update_print_report_permission(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
        if not user:
           raise HTTPException(status_code=404, detail="User not found.")
        
        user.can_print_report = True
        db.commit()
        db.refresh(user)

        return {
            "user_id":user.user_id,
            "user_name":user.user_name,
            "user_email":user.user_email,  
            "user_type" :user.user_type,
            "phone_no" :user.phone_no,
            "can_print_report": user.can_print_report,
            "can_add": user.can_add,
            "can_view" :user.can_view,
            "can_edit" :user.can_edit,
            "can_delete": user.can_delete,

        }
    
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating print report permission.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred whileupdating print report permission.")
    
#############################################
    
# class PermissionType(str, Enum):
#     PRINT_REPORT = "print_report"
#     ADD = "add"
#     VIEW = "view"
#     EDIT = "edit"
#     DELETE = "delete"

# class PermissionUpdate(BaseModel):
#     permission_type: PermissionType

# @router.put("/permissions/{user_id}", response_model=None)
# async def update_user_permission(
#     user_id: int, 
#     permission: PermissionUpdate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         user = db.query(AriyanspropertiesUser).filter(AriyanspropertiesUser.user_id == user_id).first()
        
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found.")
        
#         # Reset all permissions to False first
#         user.can_print_report = False
#         user.can_add = False
#         user.can_view = False
#         user.can_edit = False
#         user.can_delete = False
        
#         # Set only the requested permission to True
#         if permission.permission_type == PermissionType.PRINT_REPORT:
#             user.can_print_report = True
#         elif permission.permission_type == PermissionType.ADD:
#             user.can_add = True
#         elif permission.permission_type == PermissionType.VIEW:
#             user.can_view = True
#         elif permission.permission_type == PermissionType.EDIT:
#             user.can_edit = True
#         elif permission.permission_type == PermissionType.DELETE:
#             user.can_delete = True

#         db.commit()
#         db.refresh(user)

#         return {
#             "user_id": user.user_id,
#             "user_name": user.user_name,
#             "user_email": user.user_email,  
#             "user_type": user.user_type,
#             "phone_no": user.phone_no,
#             "can_print_report": user.can_print_report,
#             "can_add": user.can_add,
#             "can_view": user.can_view,
#             "can_edit": user.can_edit,
#             "can_delete": user.can_delete,
#         }
    
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(
#             status_code=500, 
#             detail=f"A database error occurred while updating {permission.permission_type} permission."
#         )
#     except Exception:
#         db.rollback()
#         raise HTTPException(
#             status_code=500, 
#             detail=f"An unexpected error occurred while updating {permission.permission_type} permission."
#         )






