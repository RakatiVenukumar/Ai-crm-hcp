from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import HCP
from app.schemas import HCPCreate, HCPUpdate


class HCPService:
    @staticmethod
    def create_hcp(db: Session, payload: HCPCreate) -> HCP:
        hcp = HCP(**payload.model_dump())
        db.add(hcp)
        db.commit()
        db.refresh(hcp)
        return hcp

    @staticmethod
    def get_hcp(db: Session, hcp_id: int) -> HCP:
        hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
        if hcp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="HCP not found",
            )
        return hcp

    @staticmethod
    def list_hcps(db: Session) -> List[HCP]:
        return db.query(HCP).order_by(HCP.created_at.desc(), HCP.id.desc()).all()

    @staticmethod
    def update_hcp(db: Session, hcp_id: int, payload: HCPUpdate) -> HCP:
        hcp = HCPService.get_hcp(db, hcp_id)

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(hcp, field, value)

        db.commit()
        db.refresh(hcp)
        return hcp

    @staticmethod
    def delete_hcp(db: Session, hcp_id: int) -> None:
        hcp = HCPService.get_hcp(db, hcp_id)
        db.delete(hcp)
        db.commit()
