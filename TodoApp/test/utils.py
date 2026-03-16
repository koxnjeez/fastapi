from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
import pytest
from fastapi.testclient import TestClient
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={'check_same_thread': False},
  poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
  db = TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()

def override_get_current_user():
  return {'username': 'koxnjeez', 'id': 1, 'role': 'admin'}

client = TestClient(app)

@pytest.fixture
def test_todo():
  todo = Todos(
    id=1,
    title='Learn coding',
    description='Everyday learning!',
    priority=4,
    complete=False,
    owner_id=1
  )

  db = TestingSessionLocal()
  db.add(todo)
  db.commit()
  yield todo
  with engine.connect() as connection:
    connection.execute(text('DELETE FROM todos;'))
    connection.commit()

@pytest.fixture
def test_user():
  user = Users(
    email='v.cherv@gmail.com',
    username='koxnjeez',
    first_name='Vlad',
    last_name='Chervonenko',
    hashed_password=bcrypt_context.hash('123123'),
    role='admin',
    phone_number='111010101002'
  )

  db = TestingSessionLocal()
  db.add(user)
  db.commit()
  yield user
  with engine.connect() as connection:
    connection.execute(text('DELETE FROM users;'))
    connection.commit()