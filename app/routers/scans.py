"""
Scans router.

This module handles creation of scan records.

This functionality is available only in MVP mode, where persistence and
authenticated user context are enabled.

Each scan is linked to a user and stored in the database.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models
from ..schemas import ScanCreate, ScanOut

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("", response_model=ScanOut)
def create_scan(
    payload: ScanCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Create a new scan record for the authenticated user.

    This endpoint is available only in MVP mode.

    Args:
        payload: Input data for the scan (pH value and details)
        db: Database session
        user: Authenticated user

    Returns:
        The created scan object.
    """

    # Create and persist a new scan linked to the current user
    scan = models.Scan(user_id=user.id, ph=payload.ph, details=payload.details)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan