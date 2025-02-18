# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from typing import List

# from api.models.property import Property
# #from api.models.propertyDetails import PropertyDetails
# from ..models.propertyContacts import PropertyContacts  
# from ..schemas import PropertyContactCreate, PropertyContactUpdate  
# from database import get_db  
# from sqlalchemy.exc import SQLAlchemyError

# router = APIRouter()

# import logging

# @router.post("/property_contacts/", response_model=None)
# def create_property_contact(
#     property_id: str,
#     property_contact: PropertyContactCreate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         # Check if the property exists
#         property_exists = db.query(Property).filter(Property.property_code == property_id).first()
#         if not property_exists:
#             raise HTTPException(status_code=404, detail="Property not found")
        
#         property_detail_exists = db.query(PropertyDetails).filter(PropertyDetails.id == property_contact.property_detail_id).first()
#         if not property_detail_exists:
#             raise HTTPException(status_code=404, detail="Property Details not found")
        
#         # Generate unique contact ID
#         count = db.query(PropertyContacts).count() + 1
#         contact_id = f"PC{count:03}"  

#         # Create new PropertyContacts entry
#         db_property_contact = PropertyContacts(
#             property_detail_id=property_detail_exists.id,
#             #contact_id=contact_id,
#             property_id=property_exists.property_code,
#             contact_person=property_contact.contact_person,
#             email=property_contact.email,
#             mobile=property_contact.mobile,
#             contact_person_address=property_contact.contact_person_address,
#         )

#         # Add to database and commit
#         db.add(db_property_contact)
#         db.commit()
#         db.refresh(db_property_contact)

#         return db_property_contact

#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         logging.error(f"SQLAlchemyError: {str(e)}")  # Log the SQLAlchemy error details
#         raise HTTPException(status_code=500, detail="A database error occurred while creating Property Contact.")
#     except Exception as e:
#         db.rollback()
#         logging.error(f"Unexpected Error: {str(e)}")  # Log the unexpected error details
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")




# @router.get("/property_contacts/", response_model=None)
# def get_all_property_contacts(db: Session = Depends(get_db)):
#     try:
#         return db.query(PropertyContacts).all()
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while get Property Contact.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while get Property Contact.")

# @router.get("/property_contacts/{contact_id}", response_model=None)
# def get_property_contact(contact_id: str, db: Session = Depends(get_db)):
#     try:
#         property_contact = db.query(PropertyContacts).filter(PropertyContacts.contact_id == contact_id).first()
#         if not property_contact:
#             raise HTTPException(status_code=404, detail="Property Contact not found")
#         return property_contact
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while get Property Contact.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while get Property Contact.")
    
# @router.put("/property_contacts/{contact_id}", response_model=None)
# def update_property_contact(
#     contact_id: str,
#     property_contact_update: PropertyContactUpdate,
#     db: Session = Depends(get_db)
# ):
#     try:
#         db_property_contact = db.query(PropertyContacts).filter(PropertyContacts.contact_id == contact_id).first()
#         if not db_property_contact:
#             raise HTTPException(status_code=404, detail="Property Contact not found")

#         if property_contact_update.property_id is not None:
#             property_exists = db.query(Property).filter(Property.property_code == property_contact_update.property_id).first()
#             if not property_exists:
#                 raise HTTPException(status_code=404, detail="The provided property_id does not exist.")
#             db_property_contact.property_id = property_contact_update.property_id

#         if property_contact_update.contact_person is not None:
#             db_property_contact.contact_person = property_contact_update.contact_person
#         if property_contact_update.email is not None:
#             db_property_contact.email = property_contact_update.email
#         if property_contact_update.mobile is not None:
#             db_property_contact.mobile = property_contact_update.mobile

#         db.commit()
#         db.refresh(db_property_contact)

#         return {"message": "Property Contact updated successfully.","property_contact":db_property_contact}

#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"A database error occurred: {str(e)}")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")



# @router.delete("/property_contacts/{contact_id}", response_model=None)
# def delete_property_contact(contact_id: str, db: Session = Depends(get_db)):
#     try:
#         db_property_contact = db.query(PropertyContacts).filter(PropertyContacts.contact_id == contact_id).first()
#         if not db_property_contact:
#             raise HTTPException(status_code=404, detail="Property Contact not found")

#         db.delete(db_property_contact)
#         db.commit()
#         return {"message": "Property Contact deleted successfully", "property_contact":db_property_contact}
#     except HTTPException as http_exc:
#         raise http_exc
#     except SQLAlchemyError as e:
#         db.rollback()
#         raise HTTPException(status_code=404, detail="A database error occurred while delete Property Contact.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred while delete Property Contact.")
