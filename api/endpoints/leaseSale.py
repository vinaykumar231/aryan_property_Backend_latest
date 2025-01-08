from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import pytz
from sqlalchemy.orm import Session
from typing import List
from database import get_db  # Database session
from ..models.leaseSale import LeaseSale
from ..schemas import LeaseSaleCreate, LeaseSaleUpdate, LeaseSaleResponse

router = APIRouter()

# POST: Create a new LeaseSale
@router.post("/lease_sale/", response_model=LeaseSaleResponse)
def create_lease_sale(
    lease_sale: LeaseSaleCreate,
    db: Session = Depends(get_db)
):
    lease_id = str(db.query(LeaseSale).count() + 1)  # Generate lease_id based on count (or use UUID)
    db_lease_sale = LeaseSale(lease_id=lease_id, lease_type=lease_sale.lease_type)
    db.add(db_lease_sale)
    db.commit()
    db.refresh(db_lease_sale)
    return db_lease_sale

# GET: Retrieve a specific LeaseSale by lease_id
@router.get("/lease_sale/{lease_id}", response_model=LeaseSaleResponse)
def get_lease_sale(
    lease_id: str,
    db: Session = Depends(get_db)
):
    db_lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == lease_id).first()
    if not db_lease_sale:
        raise HTTPException(status_code=404, detail="Lease sale not found")
    return db_lease_sale

# GET: Retrieve all LeaseSale records
@router.get("/lease_sale/", response_model=List[LeaseSaleResponse])
def get_lease_sales(db: Session = Depends(get_db)):
    lease_sales = db.query(LeaseSale).all()
    if not lease_sales:
        raise HTTPException(status_code=404, detail="No lease sales found")
    return lease_sales

# PUT: Update an existing LeaseSale
@router.put("/lease_sale/{lease_id}", response_model=LeaseSaleResponse)
def update_lease_sale(
    lease_id: str,
    lease_sale_update: LeaseSaleUpdate,
    db: Session = Depends(get_db)
):
    utc_now = pytz.utc.localize(datetime.utcnow())
    ist_now = utc_now.astimezone(pytz.timezone('Asia/Kolkata'))
    db_lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == lease_id).first()
    
    if not db_lease_sale:
        raise HTTPException(status_code=404, detail="Lease sale not found")
    
    db_lease_sale.lease_type = lease_sale_update.lease_type
    db_lease_sale.edit_date = ist_now
    db.commit()
    db.refresh(db_lease_sale)
    return db_lease_sale

# DELETE: Delete a LeaseSale by lease_id
@router.delete("/lease_sale/{lease_id}", response_model=LeaseSaleResponse)
def delete_lease_sale(
    lease_id: str,
    db: Session = Depends(get_db)
):
    db_lease_sale = db.query(LeaseSale).filter(LeaseSale.lease_id == lease_id).first()
    if not db_lease_sale:
        raise HTTPException(status_code=404, detail="Lease sale not found")

    db.delete(db_lease_sale)
    db.commit()
    return db_lease_sale
