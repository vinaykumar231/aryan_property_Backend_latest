# from datetime import datetime
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List
# from pydantic import BaseModel
# from database import get_db
# from ..models.city import City
# from ..schemas import CityCreate, CityUpdate

# router = APIRouter()



# @router.post("/city/", response_model=None)
# def create_city(
#     city: CityCreate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_city = City(city_name=city.city_name)
#         db.add(db_city)
#         db.commit()
#         db.refresh(db_city)
#         return db_city
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while adding the city.")
#     except Exception:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while adding the city.")

# @router.get("/city/{city_id}", response_model=None)
# def get_city(
#     city_id: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_city = db.query(City).filter(City.city_id == city_id).first()
#         if not db_city:
#             raise HTTPException(status_code=404, detail="City not found")
#         return db_city
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="A database error occurred while fetching the city.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching the city.")

# @router.get("/cities/", response_model=None)
# def get_cities(
#     skip: int = 0,
#     limit: int = 10,
#     db: Session = Depends(get_db)
# ):
#     try:
#         cities = db.query(City).offset(skip).limit(limit).all()
#         if not cities:
#             raise HTTPException(status_code=404, detail="No cities found")
#         return cities
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="A database error occurred while fetching cities.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching cities.")
    
# @router.get("/get_all_cities/", response_model=None)
# def get_all_cities(db: Session = Depends(get_db)):
#     try:
#         cities = db.query(City).all()
#         if not cities:
#             raise HTTPException(status_code=404, detail="No descriptions found")
#         return cities
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         raise HTTPException(status_code=500, detail="A database error occurred while fetching cities.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching cities.")

# @router.put("/city/{city_id}", response_model=None)
# def update_city(
#     city_id: int,
#     city_update: CityUpdate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_city = db.query(City).filter(City.city_id == city_id).first()
#         if not db_city:
#             raise HTTPException(status_code=404, detail="City not found")
        
#         db_city.city_name = city_update.city_name
#         db_city.edit_date = datetime.utcnow()
#         db.commit()
#         db.refresh(db_city)
#         return db_city
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while updating the city.")
#     except Exception:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the city.")

# @router.delete("/city/{city_id}", status_code=200)
# def delete_city(
#     city_id: int,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_city = db.query(City).filter(City.city_id == city_id).first()
#         if not db_city:
#             raise HTTPException(status_code=404, detail="City not found")
        
#         db.delete(db_city)
#         db.commit()
#         return {"message": "City deleted successfully.", "city_id": city_id}
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="A database error occurred while deleting the city.")
#     except Exception:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the city.")
