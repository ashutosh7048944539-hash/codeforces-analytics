from datetime import datetime, timezone
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User
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