from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from . import schemas_pack, models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter((models.User._id == user_id)).first()


def check_user(db: Session, user_id: str, pwd: str):
    return db.query(models.User).filter(
        and_((models.User.id == user_id), (models.User.hashed_password == pwd + "notreallyhashed"))).first()


def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter((models.User.phone == phone)).first()


def check_user_by_phone(db: Session, phone: str, pwd: str):
    return db.query(models.User).filter(
        and_((models.User.phone == phone), (models.User.hashed_password == pwd + "notreallyhashed"))).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter((models.User.email == email)).first()


def check_user_by_email(db: Session, email: str, pwd: str):
    return db.query(models.User).filter(
        and_((models.User.email == email), (models.User.hashed_password == pwd + "notreallyhashed"))).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas_pack.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(id=user.id, email=user.email, phone=user.phone, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas_pack.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
