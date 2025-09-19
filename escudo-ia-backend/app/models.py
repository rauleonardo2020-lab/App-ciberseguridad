from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scans = relationship("ScanResult", back_populates="user", cascade="all, delete-orphan")

class ScanResult(Base):
    __tablename__ = "scan_results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ip = Column(String(64), nullable=False, index=True)
    scan_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (UniqueConstraint("id", "user_id", name="uq_scan_user"),)

    user = relationship("User", back_populates="scans")
