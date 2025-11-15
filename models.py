from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Phone number from Twilio "From" field (e.g., "+14045551234")
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    # Emory email typed by user via SMS, must end with @emory.edu (enforced in code)
    emory_email = Column(String(255), unique=True, nullable=True)
    # True once they successfully enter the correct code from their Emory email
    is_verified = Column(Boolean, nullable=False, default=False)
    # Temporary 6-digit code we email them; cleared (set to NULL) after success
    otp_code = Column(String(6), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    # Relationship to ride requests (optional for now, but useful later)
    ride_requests = relationship("RideRequest", back_populates="user")


class RideRequest(Base):
    """
    Stub model for later when you start storing actual ride intents like
    '8:30pm, 3 people'.
    Right now we won't use it in main.py yet, but it's here for when
    you're ready to parse Body into structured data.
    """
    __tablename__ = "ride_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="ride_requests")
    # When they want to leave Emory (you'll parse from SMS later)
    requested_time = Column(DateTime, nullable=True)
    # How many people in their party (1–4), you'll fill this from SMS text
    party_size = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

