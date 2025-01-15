from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from ..models.area import Area
from ..models.sublocation import Sublocation
from ..schemas import AreaCreate, AreaUpdate, AreaResponse

router = APIRouter()


@router.post("/areas/", response_model=None)
def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    try:
        db_sublocation = db.query(Sublocation).filter(Sublocation.sublocation_id == area.sublocation_id).first()
        if not db_sublocation:
            raise HTTPException(status_code=404, detail="Sublocation not found")

        db_area = Area(
            sublocation_id=area.sublocation_id,
            area_name=area.area_name,
            edit_date=datetime.utcnow()
        )
        db.add(db_area)
        db.commit()
        db.refresh(db_area)
        return db_area
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while creating the area.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the area.")

# Get Area by ID
@router.get("/areas/{area_id}", response_model=None)
def get_area(area_id: int, db: Session = Depends(get_db)):
    try:
        db_area = db.query(Area).filter(Area.area_id == area_id).first()
        if not db_area:
            raise HTTPException(status_code=404, detail="Area not found")
        return db_area
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching the area.")

@router.get("/areas/", response_model=None)
def get_areas(db: Session = Depends(get_db)):
    try:
        areas = db.query(Area).all()
        if not areas:
            raise HTTPException(status_code=404, detail="No areas found")
        return areas
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching areas.")

@router.put("/areas/{area_id}", response_model=None)
def update_area(area_id: int, area_update: AreaUpdate, db: Session = Depends(get_db)):
    try:
        db_area = db.query(Area).filter(Area.area_id == area_id).first()
        if not db_area:
            raise HTTPException(status_code=404, detail="Area not found")

        db_area.area_name = area_update.area_name
        db_area.edit_date = datetime.utcnow()
        db.commit()
        db.refresh(db_area)
        return db_area
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating the area.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the area.")

@router.delete("/areas/{area_id}")
def delete_area(area_id: int, db: Session = Depends(get_db)):
    try:
        db_area =  db.query(Area).filter(Area.area_id == area_id).first()
        if not db_area:
            raise HTTPException(status_code=404, detail="Area not found")

        db.delete(db_area)
        db.commit()
        return {"message": "Area deleted successfully", "area_id": area_id}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the area.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the area.")
