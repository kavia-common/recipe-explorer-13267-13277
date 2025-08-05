from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    create_engine,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import database_exists, create_database

DATABASE_URL = "sqlite:///./recipes.db"  # For demonstration, replace with env later

Base = declarative_base()

# Many to Many relationship: User <-> Favorite Recipes
favorites_table = Table(
    "favorites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
)

class User(Base):
    """User model for registration and login (optional)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    favorites = relationship(
        "Recipe",
        secondary=favorites_table,
        back_populates="favorited_by_users"
    )

class Recipe(Base):
    """Recipe model."""
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    favorited_by_users = relationship(
        "User",
        secondary=favorites_table,
        back_populates="favorites"
    )

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
