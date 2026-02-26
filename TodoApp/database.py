from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# формат подключения бд: типсубд://имяпользователя:пароль@хостадрес/названиебд
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:test7777@localhost/TodoAppDB'

# connect_args={'check_same_thread': False} в аргументе только для sqlite3
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()