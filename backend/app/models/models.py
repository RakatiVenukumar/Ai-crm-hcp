from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


class HCP(Base):
    """Healthcare Professional Model"""

    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    specialization = Column(String(255), nullable=True)
    hospital = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to Interaction
    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HCP(id={self.id}, name={self.name}, specialization={self.specialization})>"


class Interaction(Base):
    """Interaction Log Model"""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    interaction_type = Column(String(255), nullable=False)
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=True)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(Text, nullable=True)
    samples_distributed = Column(Text, nullable=True)
    sentiment = Column(String(50), nullable=True)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to HCP
    hcp = relationship("HCP", back_populates="interactions")

    def __repr__(self):
        return f"<Interaction(id={self.id}, hcp_id={self.hcp_id}, interaction_type={self.interaction_type})>"
