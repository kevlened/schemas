from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Database(Base):
    __tablename__ = 'database'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    host = Column(String(250), nullable=True)
    engine = Column(String(250), nullable=False)
    username = Column(String(250), nullable=True)
    password = Column(String(250), nullable=True)