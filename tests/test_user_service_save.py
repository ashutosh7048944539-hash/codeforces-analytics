from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User
from app.services.user_service import save_user


def test_save_user_creates_user():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    user_data = {
        "handle": "test_user",
        "rating": 1200,
        "maxRating": 1300,
        "rank": "pupil",
        "maxRank": "pupil",
    }

    user = save_user(db, user_data)

    assert user.last_synced_at is not None
    assert isinstance(user.last_synced_at, datetime)

    assert user.id is not None
    assert user.handle == "test_user"
    assert user.rating == 1200
    assert user.max_rating == 1300
    assert user.rank == "pupil"
    assert user.max_rank == "pupil"

    db.close()


def test_save_user_updates_existing_user():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    first_data = {
        "handle": "test_user",
        "rating": 1200,
        "maxRating": 1300,
        "rank": "pupil",
        "maxRank": "pupil",
    }

    user = save_user(db, first_data)

    assert user.last_synced_at is not None
    assert isinstance(user.last_synced_at, datetime)

    first_id = user.id

    updated_data = {
        "handle": "test_user",
        "rating": 1400,
        "maxRating": 1450,
        "rank": "specialist",
        "maxRank": "expert",
    }

    updated_user = save_user(db, updated_data)

    assert updated_user.id == first_id
    assert updated_user.rating == 1400
    assert updated_user.max_rating == 1450
    assert updated_user.rank == "specialist"
    assert updated_user.max_rank == "expert"

    assert updated_user.last_synced_at is not None
    assert isinstance(updated_user.last_synced_at, datetime)

    users = db.query(User).all()

    assert len(users) == 1

    db.close()