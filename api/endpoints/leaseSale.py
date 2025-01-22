from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import pytz
from sqlalchemy.orm import Session
from typing import List
from database import get_db 
from ..models.leaseSale import LeaseSale
from ..schemas import LeaseSaleCreate, LeaseSaleUpdate, LeaseSaleResponse
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

@router.post("/lease_sale/", response_model=None)
def create_lease_sale(
    lease_sale: LeaseSaleCreate,
    db: Session = Depends(get_db)
):
    try:
        count = db.query(LeaseSale).count() + 1
        lease_id = f"L{count:03}"
        db_lease_sale = LeaseSale(lease_id=lease_id, lease_type=lease_sale.lease_type)
        db.add(db_lease_sale)
        db.commit()
        db.refresh(db_lease_sale)
        return db_lease_sale
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while adding Lease Sale.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while adding Lease Sale.")


@router.get("/lease_sale/{lease_id}", response_model=None)
def get_lease_sale(
    lease_id: str,
    db: Session = Depends(get_db)
):
    try:
        db_lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == lease_id).first()
        if not db_lease_sale:
            raise HTTPException(status_code=404, detail="Lease sale not found")
        return db_lease_sale
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while get Lease Sale.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while get Lease Sale.")

@router.get("/lease_sale/", response_model=None)
def get_lease_sales(db: Session = Depends(get_db)):
    try:
        lease_sales = db.query(LeaseSale).all()
        if not lease_sales:
            raise HTTPException(status_code=404, detail="No lease sales found")
        return lease_sales
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while get Lease Sale.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while get Lease Sale.")

@router.put("/lease_sale/{lease_id}", response_model=None)
def update_lease_sale(
    lease_id: str,
    lease_sale_update: LeaseSaleUpdate,
    db: Session = Depends(get_db)
):
    try:
        utc_now = pytz.utc.localize(datetime.utcnow())
        ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
        db_lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == lease_id).first()
        
        if not db_lease_sale:
            raise HTTPException(status_code=404, detail="Lease sale not found")
        
        db_lease_sale.lease_type = lease_sale_update.lease_type
        db_lease_sale.edit_date = ist_now
        db.commit()
        db.refresh(db_lease_sale)
        return {"message": "lease sale updated successfully.","lease_sale":db_lease_sale}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while update Lease Sale.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while update Lease Sale.")

@router.delete("/lease_sale/{lease_id}", response_model=None)
def delete_lease_sale(
    lease_id: str,
    db: Session = Depends(get_db)
):
    try:
        db_lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == lease_id).first()
        if not db_lease_sale:
            raise HTTPException(status_code=404, detail="Lease sale not found")

        db.delete(db_lease_sale)
        db.commit()
        return {"message": "lease sale deleted successfully.","lease_id":lease_id}
    except HTTPException as http_exc:
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail="A database error occurred while delete Lease Sale.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while delete Lease Sale.")
