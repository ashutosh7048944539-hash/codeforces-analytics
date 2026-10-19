from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User
from app.services.user_service import get_user_by_handle


def test_get_user_by_handle():
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
    )

    db.add(user)
    db.commit()

    result = get_user_by_handle(
        db,
        "test_user",
    )

    assert result is not None
    assert result.handle == "test_user"
    assert result.rating == 1200

    db.close()