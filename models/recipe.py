from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from db.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    search_query = Column(String, nullable=True, index=True)  # Store original query for matching
    history = Column(Text, nullable=True)
    technique = Column(String, nullable=True)
    glass_type = Column(String, nullable=True)
    ingredients = Column(JSON, nullable=False)
    tasting_profile = Column(JSON, nullable=True)
    method = Column(JSON, nullable=False)
    tip = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

