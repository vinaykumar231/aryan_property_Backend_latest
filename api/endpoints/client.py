from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal, engine, Base, get_db
from pydantic import BaseModel
from typing import List
from datetime import datetime
from ..models.client import Client 
from ..schemas import ClientCreate

router= APIRouter()


@router.post("/clients/", response_model=None)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    try:
        db_client = Client(
            Name=client.Name,
            Emial=client.Emial,
            Conatct_Number=client.Conatct_Number,
            Location=client.Location
        )
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while creating the client.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the client.")

# GET API to retrieve all clients
@router.get("/clients/")
def get_clients(db: Session = Depends(get_db)):
    try:
        clients = db.query(Client).all()
        
        if not clients:
            raise HTTPException(status_code=404, detail="No clients found")

        return clients
    except HTTPException as http_exc:
        raise http_exc
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
# Update an existing client
@router.put("/clients/{client_id}", response_model=None)
def update_client(client_id: int, client: ClientCreate, db: Session = Depends(get_db)):
    try:
        db_client = db.query(Client).filter(Client.client_id == client_id).first()
        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        for key, value in client.dict().items():
            setattr(db_client, key, value)
        
        db.commit()
        db.refresh(db_client)
        return db_client
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while updating the client.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the client.")

# Delete a client
@router.delete("/clients/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    try:
        db_client = db.query(Client).filter(Client.client_id == client_id).first()
        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        db.delete(db_client)
        db.commit()
        return {"message": "Client deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the client.")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the client.")