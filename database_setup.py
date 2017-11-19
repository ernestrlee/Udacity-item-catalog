import os
import sys
# Configuration for sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Class definitions, tables, and mapping
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    # Table information
    __tablename__ = 'category'
    # Mappers
    name = Column(String(80), nullable=False, unique=True)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Create serialize method for API endpoint
    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return{
            'name': self.name,
            'id': self.id
        }


class Item(Base):
    # Table information
    __tablename__ = 'item'
    # Mappers
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(500))
    imageurl = Column(String)
    category_name = Column(String, ForeignKey('category.name'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Create serialize method for API endpoint
    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return{
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'imageURL': self.imageurl,
            'category': self.category_name
        }


# Create the database
engine = create_engine('sqlite:///cataloginfo.db')

Base.metadata.create_all(engine)
