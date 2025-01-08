from sqlalchemy.orm import Session
from db.models import user_model
from db.schemas import user_schema
from sqlalchemy import or_, and_, union_all

from utils.jwt import Permission

def find_user_by_employee_id(db: Session, employee_id: str):
    return db.query(user_model.User).filter(user_model.User.employee_id == employee_id).first()

def find_user_by_userid(db: Session, user_id: int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()
