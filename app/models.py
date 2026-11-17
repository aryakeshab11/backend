from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.db import Base


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(128), index=True)
    provider = Column(String(64))
    amount_usd = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    amount_local = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    trial_expires_at = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    session_id = Column(String(128), nullable=True)
