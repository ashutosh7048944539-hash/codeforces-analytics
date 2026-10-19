from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User
from app.services.user_service import sync_user


def test_sync_user_refreshes_stale_cache():
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
        last_synced_at=(
            datetime.now(timezone.utc)
            - timedelta(minutes=31)
        ),
    )

    db.add(user)
    db.commit()

    mock_user_data = {
        "handle": "test_user",
        "rating": 1400,
        "maxRating": 1450,
        "rank": "specialist",
        "maxRank": "expert",
    }

    with patch(
        "app.services.user_service.CodeforcesClient"
    ) as MockClient:

        mock_client = MockClient.return_value
        mock_client.get_user_info.return_value = mock_user_data

        result = sync_user(
            db,
            "test_user",
        )

        mock_client.get_user_info.assert_called_once_with(
            "test_user"
        )

        mock_client.close.assert_called_once()

    assert result.rating == 1400
    assert result.max_rating == 1450
    assert result.rank == "specialist"
    assert result.max_rank == "expert"

    db.close()