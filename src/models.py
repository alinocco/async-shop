from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

Base = declarative_base()

class UserModel(Base):
    __tablename__ = 'User'

    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    is_admin = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default= True)

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'{self.username}'


users = [
    UserModel(username='admin', password='admin', is_admin=True),
]

session_maker = sessionmaker(bind = create_engine('postgresql+psycopg2://asyncshop:asyncshop@localhost/asyncshop'))

def create_users():
    with session_maker() as session:
        for user in users:
            session.add(user)
        session.commit()

def get_users():
    with session_maker() as session:
        user_records = session.query(UserModel).all()
        for user in user_records:
            print(user)

get_users()

