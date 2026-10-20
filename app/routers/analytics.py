from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from app.services.analytics_event_service import record_event
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services.analytics_service import (
    get_rating_history,
    get_solved_problem_count,
    get_solved_problems_by_difficulty,
    get_solved_problems_by_tag,
    get_success_rate_by_tag,
    get_weak_topics,
)

from app.services.user_service import (
    sync_user,
)


router = APIRouter(
    prefix="/users",
    tags=["analytics"],
)


@router.get("/{handle}/rating-history")
def rating_history(
    handle: str,
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

    return {
        "handle": user.handle,
        "rating_history": get_rating_history(
            db,
            user.id,
        ),
    }


@router.get("/{handle}/analytics")
def user_analytics(
    handle: str,
    source: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        user = sync_user(
            db,
            handle,
        )

        record_event(
            db,
            event_type="analysis_started",
            handle=user.handle,
            source=source,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    return {
        "handle": user.handle,

        "current_rating": user.rating,

        "max_rating": user.max_rating,

        "rank": user.rank,

        "max_rank": user.max_rank,

        "solved_count": get_solved_problem_count(
            db,
            user.id,
        ),

        "difficulty": get_solved_problems_by_difficulty(
            db,
            user.id,
        ),

        "tags": get_solved_problems_by_tag(
            db,
            user.id,
        ),

        "success_rate_by_tag": get_success_rate_by_tag(
            db,
            user.id,
        ),

        "weak_topics": get_weak_topics(
            db,
            user.id,
        ),
    }