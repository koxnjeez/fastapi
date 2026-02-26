from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from jose import JWTError, jwt

# в адресной строке все будет начинаться на /auth
router = APIRouter(
  prefix='/auth',
  tags=['auth']
)

# рандомный ключ - команда в терминале (openssl rand -hex 32)
SECRET_KEY = '124acb5d76c147e78cc075e4214e784c4150352b25cf35bd2f20c3635a1be66b'
ALGORITHM = 'HS256'

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close

db_dependency = Annotated[Session, Depends(get_db)]

# сетапы для хеширования пароля
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# путь получения токена авторизации
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
  email: str = Field(min_length=1, max_length=200)
  username: str = Field(min_length=1, max_length=45)
  first_name: str = Field(min_length=1, max_length=45)
  last_name: str = Field(min_length=1, max_length=45)
  password: str = Field(min_length=6, max_length=45)
  role: str | None = Field(default=None, min_length=1, max_length=45)

  model_config = {
    "json_schema_extra": {
      "example": {
        "email": "string",
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "password": "string"
      }
    }
  }

class Token(BaseModel):
  access_token: str
  token_type: str

def authenticate_user(username: str, password: str, db):
  user = db.query(Users).filter(Users.username == username).first()

  if not user:
    return False
  if not bcrypt_context.verify(password, user.hashed_password):
    return False
  return user

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
  encode = {'sub': username, 'id': user_id, 'role': role}
  expires = datetime.now(timezone.utc) + expires_delta
  encode.update({'exp': expires})
  return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get('sub')
    user_id: int = payload.get('id')
    user_role: str = payload.get('role')
    if username is None or user_id is None or user_role is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Cant validate current user')
    return {'username': username, 'id': user_id, 'role': user_role}
  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Cant validate current user')

@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
  create_user_model = Users(
    email=create_user_request.email,
    username=create_user_request.username,
    first_name=create_user_request.first_name,
    last_name=create_user_request.last_name,
    hashed_password=bcrypt_context.hash(create_user_request.password),
    role='member' if create_user_request.role is None else create_user_request.role,
    is_active=True
  )

  db.add(create_user_model)
  db.commit()

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
  user = authenticate_user(form_data.username, form_data.password, db)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                          detail='Cant validate current user')
  token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

  return {'access_token': token, 'token_type': 'bearer'}