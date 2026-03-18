"""
Trends router.

This module provides basic aggregated statistics based on user scan data.

Available only in MVP mode, since it requires:
- authenticated user context
- access to persisted scan records

Currently implemented as a simple aggregation (count, average, min, max).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from .. import models

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("")
def trends(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Calculate basic statistics for the user's scan history.

    This endpoint aggregates pH values from all scans associated with
    the authenticated user.

    Args:
        db: Database session
        user: Authenticated user

    Returns:
        Dictionary with:
        - count: number of valid scan entries
        - avg: average pH value
        - min: minimum pH value
        - max: maximum pH value
    """

    # MVP stub: compute simple statistics from stored scans
    scans = db.query(models.Scan).filter(models.Scan.user_id == user.id).all()

    values = []
    for s in scans:
        try:
            values.append(float(s.ph))
        except Exception:
            # Skip invalid or non-numeric values
            pass

    if not values:
        return {"count": 0, "avg": None, "min": None, "max": None}

    return {
        "count": len(values),
        "avg": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
    }