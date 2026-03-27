from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import InteractionCreate, InteractionResponse, InteractionUpdate
from app.services.interaction_service import InteractionService

router = APIRouter(prefix="/interaction", tags=["interaction"])


@router.post("/log", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def log_interaction(payload: InteractionCreate, db: Session = Depends(get_db)) -> InteractionResponse:
    return InteractionService.create_interaction(db, payload)


@router.post("/edit/{interaction_id}", response_model=InteractionResponse)
def edit_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
) -> InteractionResponse:
    return InteractionService.edit_interaction(db, interaction_id, payload)


@router.get("/timeline", response_model=List[InteractionResponse])
def get_interaction_timeline(db: Session = Depends(get_db)) -> List[InteractionResponse]:
    return InteractionService.get_timeline(db)


@router.get("/{hcp_id}", response_model=List[InteractionResponse])
def get_interactions_for_hcp(hcp_id: int, db: Session = Depends(get_db)) -> List[InteractionResponse]:
    return InteractionService.get_interactions_by_hcp(db, hcp_id)
