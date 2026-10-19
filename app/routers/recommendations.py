from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.recommendation_service import (
    get_recommendations,
)


router = APIRouter(
    prefix="/users",
    tags=["recommendations"],
)


@router.get("/{handle}/recommendations")
def recommendations(
    handle: str,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            func.lower(User.handle) == handle.lower()
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 50",
        )

    return {
        "handle": user.handle,
        "recommendations": get_recommendations(
            db,
            user.id,
            limit,
        ),
    }