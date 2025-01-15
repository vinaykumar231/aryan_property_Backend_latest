from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from ..models.companies import Companies
from pydantic import BaseModel
from ..schemas import CompanyCreate, CompanyUpdate 
# Schemas


router = APIRouter()

@router.post("/companies/", response_model=None)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    try:
        db_company = Companies(
            company_name=company.company_name,
            contact_person=company.contact_person,
            address=company.address
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while creating the company.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the company.")

@router.get("/companies/{company_id}", response_model=None)
def get_company(company_id: int, db: Session = Depends(get_db)):
    try:
        db_company = db.query(Companies).filter(Companies.company_id == company_id).first()
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")
        return db_company
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching the company.")


@router.get("/companies/", response_model=None)
def get_companies(db: Session = Depends(get_db)):
    try:
        companies = db.query(Companies).all()
        if not companies:
            raise HTTPException(status_code=404, detail="No companies found")
        return companies
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="A database error occurred while fetching companies.")

# Update Company
@router.put("/companies/{company_id}", response_model=None)
def update_company(company_id: int, company_update: CompanyUpdate, db: Session = Depends(get_db)):
    try:
        db_company = db.query(Companies).filter(Companies.company_id == company_id).first()
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        db_company.company_name = company_update.company_name
        db_company.contact_person = company_update.contact_person
        db_company.address = company_update.address
        db.commit()
        db.refresh(db_company)
        return db_company
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating the company.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the company.")

# Delete Company
@router.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    try:
        db_company = db.query(Companies).filter(Companies.company_id == company_id).first()
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        db.delete(db_company)
        db.commit()
        return {"message": "Company deleted successfully", "company_id": company_id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the company.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the company.")
