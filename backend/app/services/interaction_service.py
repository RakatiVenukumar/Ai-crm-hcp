from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import HCP, Interaction
from app.schemas import InteractionCreate, InteractionUpdate


class InteractionService:
    @staticmethod
    def create_interaction(db: Session, payload: InteractionCreate) -> Interaction:
        hcp = db.query(HCP).filter(HCP.id == payload.hcp_id).first()
        if hcp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="HCP not found",
            )

        interaction = Interaction(**payload.model_dump())
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def edit_interaction(db: Session, interaction_id: int, payload: InteractionUpdate) -> Interaction:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
        if interaction is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Interaction not found",
            )

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(interaction, field, value)

        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def get_interactions_by_hcp(db: Session, hcp_id: int) -> List[Interaction]:
        return (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.created_at.desc())
            .all()
        )

    @staticmethod
    def get_timeline(db: Session) -> List[Interaction]:
        return (
            db.query(Interaction)
            .order_by(Interaction.created_at.desc(), Interaction.id.desc())
            .all()
        )
