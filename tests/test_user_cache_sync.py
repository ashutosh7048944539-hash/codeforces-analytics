from datetime import datetime, timezone
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Rating, Submission, User
from app.services.user_service import sync_user


def test_sync_user_uses_fresh_cache():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    user = User(
        handle="test_user",
        rating=1200,
        max_rating=1300,
        rank="pupil",
        max_rank="pupil",
        last_synced_at=datetime.now(timezone.utc),
    )

    db.add(user)
    db.commit()

    db.add(
        Rating(
            user_id=user.id,
            contest_id=1,
            contest_name="Test Contest",
            old_rating=1100,
            new_rating=1200,
            rank=100,
        )
    )

    db.add(
        Submission(
            user_id=user.id,
            contest_id=1,
            problem_index="A",
            problem_name="Test Problem",
            verdict="OK",
            programming_language="C++",
            submission_time=1000,
        )
    )

    db.commit()

    with patch(
        "app.services.user_service.CodeforcesClient"
    ) as MockClient:

        mock_client = MockClient.return_value

        result = sync_user(
            db,
            "test_user",
        )

        mock_client.get_user_info.assert_not_called()

    assert result.handle == "test_user"
    assert result.rating == 1200

    db.close()


def test_sync_user_refreshes_when_analytics_data_is_missing():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    user = User(
        handle="test_user",
        rating=1200,
        max_rating=1300,
        rank="pupil",
        max_rank="pupil",
        last_synced_at=datetime.now(timezone.utc),
    )

    db.add(user)
    db.commit()

    with patch(
        "app.services.user_service.CodeforcesClient"
    ) as MockClient:

        mock_client = MockClient.return_value

        mock_client.get_user_info.return_value = {
            "handle": "test_user",
            "rating": 1250,
            "maxRating": 1350,
            "rank": "pupil",
            "maxRank": "pupil",
        }

        mock_client.get_user_rating.return_value = []

        mock_client.get_user_submissions.return_value = []

        sync_user(
            db,
            "test_user",
        )

        mock_client.get_user_info.assert_called_once()
        mock_client.get_user_rating.assert_called_once()
        mock_client.get_user_submissions.assert_called_once()

    db.close()