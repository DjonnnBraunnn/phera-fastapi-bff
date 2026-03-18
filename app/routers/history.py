"""
History router.

This module provides access to the user's scan history.

Available only in MVP mode, since it requires:
- authenticated user context
- database persistence

Returns a list of scans associated with the current user.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models
from ..schemas import HistoryOut, ScanOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=HistoryOut)
def list_history(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Retrieve scan history for the authenticated user.

    This endpoint returns all scans associated with the current user,
    ordered from newest to oldest.

    Args:
        db: Database session
        user: Authenticated user

    Returns:
        A list of scan records.
    """

    # Query scans for the current user ordered by creation time (latest first)
    scans = (
        db.query(models.Scan)
        .filter(models.Scan.user_id == user.id)
        .order_by(models.Scan.created_at.desc())
        .all()
    )
    return {"items": scans}