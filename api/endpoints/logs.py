from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from ..models.logs import Logs  # Import your Logs model
from database import get_db  # Assuming you have a database dependency to get DB session

router = APIRouter()


def format_date(date):
    return date.strftime('%d-%m-%y %H:%M:%S') if date else None


@router.get("/get_all_logs", response_model=list)  # Define a proper response model later
async def get_all_logs(db: Session = Depends(get_db)):
    try:
        logs = db.query(Logs).options(joinedload(Logs.user)).all()  # Fetch all logs from the database
        
        if not logs:
            raise HTTPException(status_code=404, detail="No logs found.")

        # Process logs while handling possible NULL user references
        log_list = []
        for log in logs:
            log_list.append({
                "log_id": log.log_id,
                #"user_id": log.user.user_id if log.user else None,  # Handle NoneType safely
                "user_name": log.user.user_name if log.user else "Unknown",  # Provide fallback
                #"property_id": log.property_id,  # Uncomment if needed
                "action": log.action,
                "timestamp": format_date(log.timestamp) if log.timestamp else None
            })

        return log_list

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while fetching logs.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while fetching logs: {str(e)}")
    
@router.delete("/delete_log/{log_id}", response_model=None)
async def delete_log(log_id: int, db: Session = Depends(get_db)):
    try:
        # Fetch the log to be deleted
        log = db.query(Logs).filter(Logs.log_id == log_id).first()

        if not log:
            raise HTTPException(status_code=404, detail="Log not found.")

        # Delete the log entry
        db.delete(log)
        db.commit()

        return {"message": "Log deleted successfully.", "log_id": log_id}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred while deleting the log.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the log.")

