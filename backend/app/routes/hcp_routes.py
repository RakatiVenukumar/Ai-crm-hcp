from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HCPCreate, HCPResponse, HCPUpdate
from app.services.hcp_service import HCPService

router = APIRouter(prefix="/hcp", tags=["hcp"])


@router.post("", response_model=HCPResponse, status_code=status.HTTP_201_CREATED)
def create_hcp(payload: HCPCreate, db: Session = Depends(get_db)) -> HCPResponse:
    return HCPService.create_hcp(db, payload)


@router.get("", response_model=List[HCPResponse])
def list_hcps(db: Session = Depends(get_db)) -> List[HCPResponse]:
    return HCPService.list_hcps(db)


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)) -> HCPResponse:
    return HCPService.get_hcp(db, hcp_id)


@router.put("/{hcp_id}", response_model=HCPResponse)
def update_hcp(
    hcp_id: int,
    payload: HCPUpdate,
    db: Session = Depends(get_db),
) -> HCPResponse:
    return HCPService.update_hcp(db, hcp_id, payload)


@router.delete("/{hcp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hcp(hcp_id: int, db: Session = Depends(get_db)) -> Response:
    HCPService.delete_hcp(db, hcp_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
