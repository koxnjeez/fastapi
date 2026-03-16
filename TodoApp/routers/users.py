from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from pydantic import BaseModel, Field
from ..models import Users
from passlib.context import CryptContext
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
  prefix='/users',
  tags=['users']
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class PasswordVerify(BaseModel):
  actual_password: str
  new_password: str = Field(min_length=6, max_length=45)

@router.get('/profile', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication failed')

  return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put('/profile/change_pass/', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          password_verify: PasswordVerify):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication failed')

  user_model = db.query(Users).filter(Users.id == user.get('id')).first()

  if not bcrypt_context.verify(password_verify.actual_password, user_model.hashed_password):
    raise HTTPException(status_code=401, detail='Password change error.')

  user_model.hashed_password = bcrypt_context.hash(password_verify.new_password)
  db.add(user_model)
  db.commit()

@router.put('/profile/{phone_number}', status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(db: db_dependency, user: user_dependency, phone_number: str):
  if user is None:
    raise HTTPException(status_code=401, detail='Authentication failed')

  user_model = db.query(Users).filter(Users.id == user.get('id')).first()

  user_model.phone_number = phone_number
  db.add(user_model)
  db.commit()