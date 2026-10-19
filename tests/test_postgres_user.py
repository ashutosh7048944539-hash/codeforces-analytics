from app.database import SessionLocal
from app.models import User
from app.services.user_service import save_user


def test_save_user_postgres():
    db = SessionLocal()

    try:
        user_data = {
            "handle": "postgres_test_user",
            "rating": 1200,
            "maxRating": 1300,
            "rank": "pupil",
            "maxRank": "pupil",
        }

        user = save_user(
            db,
            user_data,
        )

        assert user.id is not None
        assert user.handle == "postgres_test_user"
        assert user.rating == 1200

        saved_user = (
            db.query(User)
            .filter(User.handle == "postgres_test_user")
            .first()
        )

        assert saved_user is not None
        assert saved_user.rating == 1200

    finally:
        db.query(User).filter(
            User.handle == "postgres_test_user"
        ).delete()

        db.commit()
        db.close()