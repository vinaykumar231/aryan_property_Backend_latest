# from datetime import datetime
# from fastapi import APIRouter, HTTPException, Depends
# import pytz
# from sqlalchemy.orm import Session,joinedload
# from sqlalchemy.exc import SQLAlchemyError
# from api.models.description import Description
# from api.models.property import Property
# from api.models.underconstruction import Underconstruction
# from database import get_db
# from pydantic import BaseModel
# from ..schemas import UnderconstructionCreate, UnderconstructionUpdate 

# router = APIRouter()

# @router.post("/underconstruction/", response_model=None)
# def create_underconstruction(underconstruction: UnderconstructionCreate, db: Session = Depends(get_db)):
#     try:
#         # Check if the property_code exists in the Property table
#         property_exists = db.query(Property).filter(Property.property_code == underconstruction.property_code).first()
#         if not property_exists:
#             raise HTTPException(status_code=400, detail="Property code does not exist.")

#         # Check if the description exists
#         db_description = db.query(Description).filter(Description.des_id == underconstruction.des_id).first()
#         if not db_description:
#             raise HTTPException(status_code=404, detail="Description not found")

#         # Get the current time in IST timezone
#         utc_now = datetime.utcnow()
#         utc_now = pytz.utc.localize(utc_now)  # Localize to UTC first
#         ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))  # Convert to IST

#         # Create the new Underconstruction record
#         new_uc = Underconstruction(
#             property_code=underconstruction.property_code,
#             year=underconstruction.year,
#             des_id=underconstruction.des_id,
#             edit_date=ist_now
#         )

#         db.add(new_uc)
#         db.commit()
#         db.refresh(new_uc)
        
#         return new_uc
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while creating underconstruction record.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while creating underconstruction record.")
    
# @router.get("/underconstruction/{uc_id}", response_model=None)
# def get_underconstruction(uc_id: int, db: Session = Depends(get_db)):
#     try:
#         # Fetch the Underconstruction record along with related 'Description' and 'Property' details
#         db_uc = db.query(Underconstruction).options(
#             joinedload(Underconstruction.property),  # Load related 'Property' data
#             joinedload(Underconstruction.description)  # Load related 'Description' data
#         ).filter(Underconstruction.uc_id == uc_id).first()

#         if not db_uc:
#             raise HTTPException(status_code=404, detail="Underconstruction record not found")

#         return db_uc
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="A database error occurred while fetching underconstruction record.")

# @router.get("/get_all_underconstruction/", response_model=None)
# def get_all_underconstructions(db: Session = Depends(get_db)):
#     try:
#         # Using joinedload to fetch related 'Description' and 'Property' details
#         underconstructions = db.query(Underconstruction).options(
#             joinedload(Underconstruction.property),  # Load related 'Property' data
#             joinedload(Underconstruction.description)  # Load related 'Description' data
#         ).all()
        
#         if not underconstructions:
#             raise HTTPException(status_code=404, detail="No underconstruction records found")
        
#         return underconstructions
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="A database error occurred while fetching underconstruction records.")

# @router.put("/underconstruction/{uc_id}", response_model=None)
# def update_underconstruction(uc_id: int, uc_update: UnderconstructionUpdate, db: Session = Depends(get_db)):
#     try:
#         db_uc = db.query(Underconstruction).filter(Underconstruction.uc_id == uc_id).first()
#         if not db_uc:
#             raise HTTPException(status_code=404, detail="Underconstruction record not found")
        
#         property_exists = db.query(Underconstruction).filter(Underconstruction.property_code == uc_update.property_code).first()
        
#         if property_exists:
#             raise HTTPException(status_code=400, detail="Property code does not exists.")
        
#         db_description = db.query(Description).filter(Description.des_id == uc_update.des_id).first()
#         if not db_description:
#             raise HTTPException(status_code=404, detail="Description not found")
    
#         db_uc.property_code=property_exists,
#         db_uc.year = uc_update.year
#         db_uc.des_id = uc_update.des_id
#         db.commit()
#         db.refresh(db_uc)
#         return db_uc
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while updating underconstruction record.")
#     except Exception:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while updating underconstruction record.")

# @router.delete("/underconstruction/{uc_id}")
# def delete_underconstruction(uc_id: int, db: Session = Depends(get_db)):
#     try:
#         db_uc = db.query(Underconstruction).filter(Underconstruction.uc_id == uc_id).first()
#         if not db_uc:
#             raise HTTPException(status_code=404, detail="Underconstruction record not found")

#         db.delete(db_uc)
#         db.commit()
#         return {"message": "Underconstruction record deleted successfully", "uc_id": uc_id}
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while deleting underconstruction record.")
#     except Exception:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting underconstruction record.")
