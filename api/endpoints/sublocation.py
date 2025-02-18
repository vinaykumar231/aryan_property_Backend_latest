# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from database import get_db
# from ..models.sublocation import Sublocation
# from ..models.city import City
# from ..schemas import SublocationCreate, SublocationUpdate
# from sqlalchemy.exc import SQLAlchemyError
# from datetime import datetime

# router = APIRouter()

# @router.post("/sublocation/", response_model=None)
# def create_sublocation(
#     sublocation: SublocationCreate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_city = db.query(City).filter(City.city_id == sublocation.city_id).first()
#         if not db_city:
#             raise HTTPException(status_code=404, detail="City not found")
        
#         db_sublocation = Sublocation(
#             sublocation_name=sublocation.sublocation_name,
#             city_id=sublocation.city_id
#         )
#         db.add(db_sublocation)
#         db.commit()
#         db.refresh(db_sublocation)
#         return db_sublocation
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while adding sublocation.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while adding sublocation.")

# @router.get("/sublocation/{sublocation_id}", response_model=None)
# def get_sublocation(
#     sublocation_id: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_sublocation = db.query(Sublocation).filter(Sublocation.sublocation_id == sublocation_id).first()
#         if not db_sublocation:
#             raise HTTPException(status_code=404, detail="Sublocation not found")
#         return db_sublocation
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while fetching sublocation.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching sublocation.")

# @router.get("/sublocations/", response_model=None)
# def get_sublocations(db: Session = Depends(get_db)):
#     try:
#         sublocations = db.query(Sublocation).all()
#         if not sublocations:
#             raise HTTPException(status_code=404, detail="No sublocations found")
#         return sublocations
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while fetching sublocations.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching sublocations.")

# @router.put("/sublocation/{sublocation_id}", response_model=None)
# def update_sublocation(
#     sublocation_id: int,
#     sublocation_update: SublocationUpdate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_sublocation = db.query(Sublocation).filter(Sublocation.sublocation_id == sublocation_id).first()
#         if not db_sublocation:
#             raise HTTPException(status_code=404, detail="Sublocation not found")
        
#         db_sublocation.sublocation_name = sublocation_update.sublocation_name
#         db_sublocation.edit_date = datetime.utcnow()
#         db.commit()
#         db.refresh(db_sublocation)
#         return {"message": "Sublocation updated successfully.", "sublocation": db_sublocation}
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while updating sublocation.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while updating sublocation.")

# @router.delete("/sublocation/{sublocation_id}", response_model=None)
# def delete_sublocation(
#     sublocation_id: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_sublocation = db.query(Sublocation).filter(Sublocation.sublocation_id == sublocation_id).first()
#         if not db_sublocation:
#             raise HTTPException(status_code=404, detail="Sublocation not found")
        
#         db.delete(db_sublocation)
#         db.commit()
#         return {"message": "Sublocation deleted successfully.", "sublocation": db_sublocation}
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while deleting sublocation.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting sublocation.")
