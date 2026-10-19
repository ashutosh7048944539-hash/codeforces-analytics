from datetime import datetime, timedelta, timezone

from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services.user_service import sync_user
from app.models import Rating

def test_sync_user():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    mock_user_data = {
        "handle": "test_user",
        "rating": 1200,
        "maxRating": 1300,
        "rank": "pupil",
        "maxRank": "pupil",
    }

    with patch(
        "app.services.user_service.CodeforcesClient"
    ) as MockClient:

        mock_client = MockClient.return_value

        mock_client.get_user_info.return_value = mock_user_data

        user = sync_user(
            db,
            "test_user",
        )

        mock_client.get_user_info.assert_called_once_with(
            "test_user"
        )

        mock_client.close.assert_called_once()

    assert user.handle == "test_user"
    assert user.rating == 1200
    assert user.max_rating == 1300
    assert user.rank == "pupil"
    assert user.max_rank == "pupil"

    db.close()

def test_sync_user_saves_rating_history():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    mock_user_data = {
        "handle": "test_user",
        "rating": 1300,
        "maxRating": 1300,
        "rank": "pupil",
        "maxRank": "pupil",
    }

    mock_rating_data = [
        {
            "contestId": 100,
            "contestName": "Contest A",
            "oldRating": 1200,
            "newRating": 1250,
            "rank": 5000,
        },
        {
            "contestId": 101,
            "contestName": "Contest B",
            "oldRating": 1250,
            "newRating": 1300,
            "rank": 3000,
        },
    ]

    with patch(
        "app.services.user_service.CodeforcesClient"
    ) as MockClient:
        mock_client = MockClient.return_value

        mock_client.get_user_info.return_value = mock_user_data
        mock_client.get_user_rating.return_value = mock_rating_data

        user = sync_user(
            db,
            "test_user",
        )

        mock_client.get_user_info.assert_called_once_with(
            "test_user"
        )

        mock_client.get_user_rating.assert_called_once_with(
            "test_user"
        )

        mock_client.close.assert_called_once()

    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user.id)
        .all()
    )

    assert len(ratings) == 2
    assert ratings[0].contest_id == 100
    assert ratings[0].new_rating == 1250
    assert ratings[1].contest_id == 101
    assert ratings[1].new_rating == 1300

    db.close()

def test_sync_user_does_not_duplicate_ratings():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    mock_user_data = {
        "handle": "test_user",
        "rating": 1300,
        "maxRating": 1300,
        "rank": "pupil",
        "maxRank": "pupil",
    }

    mock_rating_data = [
        {
            "contestId": 100,
            "contestName": "Contest A",
            "oldRating": 1200,
            "newRating": 1250,
            "rank": 5000,
        },
    ]

    with patch(
        "app.services.user_service.CodeforcesClient"
    ) as MockClient:
        mock_client = MockClient.return_value

        mock_client.get_user_info.return_value = mock_user_data
        mock_client.get_user_rating.return_value = mock_rating_data

        # First sync
        user = sync_user(
            db,
            "test_user",
        )

        # Make the cache stale so the second sync actually
        # calls Codeforces again.
        user.last_synced_at = (
            datetime.now(timezone.utc) - timedelta(minutes=31)
        )
        db.commit()

        # Second sync
        sync_user(
            db,
            "test_user",
        )

    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user.id)
        .all()
    )

    assert len(ratings) == 1

    db.close()