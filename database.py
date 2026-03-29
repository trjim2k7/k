import uuid
from datetime import date
from typing import AsyncGenerator, Dict, Any, List

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Date,
    Integer,
    ForeignKey,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship

from config import settings  # Assuming config.py defines a settings object with DATABASE_URL

# --- SQLAlchemy Engine and Session Setup ---
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,  # Set to True in development for SQL logging
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

async_session_maker = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SQLBase = declarative_base()

# --- Dependency for FastAPI to get a database session ---
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that provides an `AsyncSession` for database interactions
    and ensures it's properly closed after use.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# --- SQLAlchemy ORM Models ---

class User(SQLBase):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    id: Column[uuid.UUID] = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    email: Column[str] = Column(String, unique=True, nullable=False, index=True)
    password_hash: Column[str] = Column(String, nullable=False)  # Store hashed passwords
    preferences: Column[Dict[str, Any]] = Column(JSONB, nullable=True)
    created_at: Column[DateTime] = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Column[DateTime] = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define one-to-many relationship with Trip
    trips: relationship[List["Trip"]] = relationship(
        "Trip", back_populates="user", cascade="all, delete-orphan", lazy="noload"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class Trip(SQLBase):
    """
    Represents a trip planned by a user.
    """
    __tablename__ = "trips"

    id: Column[uuid.UUID] = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Column[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Column[str] = Column(String, nullable=False)
    destination: Column[str] = Column(String, nullable=False)
    start_date: Column[date] = Column(Date, nullable=False)
    end_date: Column[date] = Column(Date, nullable=False)
    num_travelers: Column[int] = Column(Integer, nullable=False)
    travel_style: Column[str] = Column(String, nullable=True)
    interests: Column[List[str]] = Column(ARRAY(String), nullable=True)
    budget_range: Column[str] = Column(String, nullable=True)
    status: Column[str] = Column(String, nullable=False, default="planning") # e.g., 'planning', 'booked', 'completed'
    created_at: Column[DateTime] = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Column[DateTime] = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define many-to-one relationship with User
    user: relationship["User"] = relationship("User", back_populates="trips", lazy="noload")

    # Define one-to-many relationship with Itinerary
    itineraries: relationship[List["Itinerary"]] = relationship(
        "Itinerary", back_populates="trip", cascade="all, delete-orphan", lazy="noload"
    )

    def __repr__(self):
        return f"<Trip(id={self.id}, name='{self.name}', destination='{self.destination}')>"

class Itinerary(SQLBase):
    """
    Represents a detailed itinerary for a specific trip.
    """
    __tablename__ = "itineraries"

    id: Column[uuid.UUID] = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    trip_id: Column[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False
    )
    name: Column[str] = Column(String, nullable=False)
    description: Column[str] = Column(String, nullable=True)
    # 'days' is an array of objects, each with 'date' and 'activities'
    # Example: [{"date": "2023-01-01", "activities": [{"time": "09:00", "description": "Activity 1"}]}]
    days: Column[List[Dict[str, Any]]] = Column(JSONB, nullable=False)
    created_at: Column[DateTime] = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Column[DateTime] = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Define many-to-one relationship with Trip
    trip: relationship["Trip"] = relationship("Trip", back_populates="itineraries", lazy="noload")

    def __repr__(self):
        return f"<Itinerary(id={self.id}, name='{self.name}')>"

# --- Utility Functions for Development/Testing ---

async def create_all_tables() -> None:
    """
    Asynchronously creates all tables defined in SQLBase in the database.
    Use with caution, primarily for development or testing environments.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLBase.metadata.create_all)
    print("All tables created successfully.")

async def drop_all_tables() -> None:
    """
    Asynchronously drops all tables defined in SQLBase from the database.
    Use with EXTREME caution, only for development or testing environments
    as it will delete all data.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLBase.metadata.drop_all)
    print("All tables dropped successfully.")

# Note on password hashing:
# The `password_hash` column is defined to store a hashed password.
# It is critical that actual password hashing (e.g., using bcrypt or Argon2)
# is performed in the application's service layer BEFORE a User object
# is created or updated and committed to the database. The database layer
# itself only stores the resulting hash, not the plaintext password.