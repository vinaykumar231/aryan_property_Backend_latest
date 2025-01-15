from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from api.models.underconstruction import Underconstruction
from database import get_db
from pydantic import BaseModel
from ..schemas import UnderconstructionCreate, UnderconstructionUpdate 

router = APIRouter()

@router.post("/underconstruction/", response_model=None)
def create_underconstruction(uc: UnderconstructionCreate, db: Session = Depends(get_db)):
    try:
        db_uc = Underconstruction(
            year=uc.year,
            des_id=uc.des_id
        )
        db.add(db_uc)
        db.commit()
        db.refresh(db_uc)
        return db_uc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while creating underconstruction record.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating underconstruction record.")

@router.get("/underconstruction/{uc_id}", response_model=None)
def get_underconstruction(uc_id: int, db: Session = Depends(get_db)):
    try:
        db_uc = db.query(Underconstruction).filter(Underconstruction.uc_id == uc_id).first()
        if not db_uc:
            raise HTTPException(status_code=404, detail="Underconstruction record not found")
        return db_uc
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching underconstruction record.")

@router.get("/underconstruction/", response_model=None)
def get_underconstructions(db: Session = Depends(get_db)):
    try:
        underconstructions = db.query(Underconstruction).all()
        if not underconstructions:
            raise HTTPException(status_code=404, detail="No underconstruction records found")
        return underconstructions
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching underconstruction records.")

@router.put("/underconstruction/{uc_id}", response_model=None)
def update_underconstruction(uc_id: int, uc_update: UnderconstructionUpdate, db: Session = Depends(get_db)):
    try:
        db_uc = db.query(Underconstruction).filter(Underconstruction.uc_id == uc_id).first()
        if not db_uc:
            raise HTTPException(status_code=404, detail="Underconstruction record not found")

        db_uc.year = uc_update.year
        db_uc.des_id = uc_update.des_id
        db.commit()
        db.refresh(db_uc)
        return db_uc
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating underconstruction record.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating underconstruction record.")

@router.delete("/underconstruction/{uc_id}")
def delete_underconstruction(uc_id: int, db: Session = Depends(get_db)):
    try:
        db_uc = db.query(Underconstruction).filter(Underconstruction.uc_id == uc_id).first()
        if not db_uc:
            raise HTTPException(status_code=404, detail="Underconstruction record not found")

        db.delete(db_uc)
        db.commit()
        return {"message": "Underconstruction record deleted successfully", "uc_id": uc_id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting underconstruction record.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting underconstruction record.")
