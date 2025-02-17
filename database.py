from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class LinkedInExample(Base):
    __tablename__ = 'linkedin_examples'
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TwitterExample(Base):
    __tablename__ = 'twitter_examples'
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InstagramExample(Base):
    __tablename__ = 'instagram_examples'
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LinkedInTransformation(Base):
    __tablename__ = 'linkedin_transformations'
    id = Column(String, primary_key=True)
    original_text = Column(Text, nullable=False)
    transformed_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TwitterTransformation(Base):
    __tablename__ = 'twitter_transformations'
    id = Column(String, primary_key=True)
    original_text = Column(Text, nullable=False)
    transformed_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InstagramTransformation(Base):
    __tablename__ = 'instagram_transformations'
    id = Column(String, primary_key=True)
    original_text = Column(Text, nullable=False)
    transformed_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    engine = create_engine('sqlite:///social_sculptor.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)() 