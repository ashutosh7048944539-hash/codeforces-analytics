from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Problem, Rating, Submission, User


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)

    return engine, SessionLocal


def test_rating_history_endpoint():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    user = User(
        handle="test_user",
        rating=1300,
        max_rating=1300,
        rank="pupil",
        max_rank="pupil",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(
        Rating(
            user_id=user.id,
            contest_id=100,
            contest_name="Contest A",
            old_rating=1200,
            new_rating=1250,
            rank=5000,
        )
    )

    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get(
        "/users/test_user/rating-history"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["handle"] == "test_user"
    assert len(data["rating_history"]) == 1
    assert data["rating_history"][0]["contest_id"] == 100
    assert data["rating_history"][0]["new_rating"] == 1250

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()


def test_rating_history_user_not_found():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get(
        "/users/does_not_exist/rating-history"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "User not found"
    }

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()


def test_user_analytics_endpoint(monkeypatch):
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(
        Problem(
            contest_id=100,
            problem_index="A",
            name="Test Problem",
            rating=1000,
            tags="dp,greedy",
        )
    )

    db.add(
        Submission(
            user_id=user.id,
            contest_id=100,
            problem_index="A",
            problem_name="Test Problem",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1000,
        )
    )

    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    def fake_sync_user(db, handle):
        return user

    monkeypatch.setattr(
        "app.routers.analytics.sync_user",
        fake_sync_user,
    )

    response = client.get(
        "/users/testuser/analytics"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["handle"] == "testuser"
    assert data["solved_count"] == 1
    assert data["difficulty"] == {
        "1000": 1
    }
    assert data["tags"] == {
        "dp": 1,
        "greedy": 1,
    }
    assert data["success_rate_by_tag"] == {
        "dp": 1.0,
        "greedy": 1.0,
    }
    assert data["weak_topics"] == []

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()