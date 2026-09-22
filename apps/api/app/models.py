from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    full_name: Mapped[str]=mapped_column(String(150))
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True)
    phone: Mapped[str]=mapped_column(String(30))
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
    farms: Mapped[list["Farm"]]=relationship(back_populates="owner",cascade="all, delete-orphan")

class Farm(Base):
    __tablename__="farms"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"))
    name: Mapped[str]=mapped_column(String(150))
    location: Mapped[str]=mapped_column(String(150))
    farm_type: Mapped[str]=mapped_column(String(50))
    size_hectares: Mapped[float|None]=mapped_column(Float,nullable=True)
    primary_activity: Mapped[str]=mapped_column(String(150))
    owner: Mapped[User]=relationship(back_populates="farms")
    records: Mapped[list["FarmRecord"]]=relationship(back_populates="farm",cascade="all, delete-orphan")

class FarmRecord(Base):
    __tablename__="farm_records"
    id: Mapped[int]=mapped_column(primary_key=True)
    farm_id: Mapped[int]=mapped_column(ForeignKey("farms.id"))
    activity: Mapped[str]=mapped_column(String(100))
    crop_or_livestock: Mapped[str]=mapped_column(String(100))
    notes: Mapped[str]=mapped_column(Text,default="")
    farm: Mapped[Farm]=relationship(back_populates="records")
