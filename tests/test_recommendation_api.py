from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Problem, Submission, User


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


def test_recommendations_endpoint():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    user = User(
        handle="testuser",
        rating=1000,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    problems = [
        Problem(
            contest_id=1,
            problem_index="A",
            name="Solved DP Problem",
            rating=1200,
            tags="dp",
        ),
        Problem(
            contest_id=2,
            problem_index="A",
            name="Weak DP Problem",
            rating=1150,
            tags="dp",
        ),
        Problem(
            contest_id=3,
            problem_index="A",
            name="Weak DP Problem 2",
            rating=1100,
            tags="dp",
        ),
        Problem(
            contest_id=4,
            problem_index="A",
            name="Weak DP Problem 3",
            rating=1200,
            tags="dp",
        ),
    ]

    db.add_all(problems)
    db.commit()

    submissions = [
        Submission(
            user_id=user.id,
            contest_id=1,
            problem_index="A",
            problem_name="Solved DP Problem",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1000,
        ),
        Submission(
            user_id=user.id,
            contest_id=2,
            problem_index="A",
            problem_name="Weak DP Problem",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=2000,
        ),
        Submission(
            user_id=user.id,
            contest_id=3,
            problem_index="A",
            problem_name="Weak DP Problem 2",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=3000,
        ),
        Submission(
            user_id=user.id,
            contest_id=4,
            problem_index="A",
            problem_name="Weak DP Problem 3",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=4000,
        ),
    ]

    db.add_all(submissions)
    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get(
        "/users/testuser/recommendations"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["handle"] == "testuser"

    assert len(
        data["recommendations"]
    ) == 3

    for recommendation in data["recommendations"]:
        assert recommendation["rating"] in {
            1100,
            1150,
            1200,
        }

        assert "dp" in recommendation["tags"]

        assert recommendation["score"] > 0

        assert "weak" in (
            recommendation["reason"].lower()
        )

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()


def test_recommendations_endpoint_user_not_found():
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
        "/users/does_not_exist/recommendations"
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "User not found"
    }

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()


def test_recommendations_endpoint_limit():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    user = User(
        handle="testuser",
        rating=1000,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    problems = [
        Problem(
            contest_id=1,
            problem_index="A",
            name="DP 1",
            rating=1100,
            tags="dp",
        ),
        Problem(
            contest_id=2,
            problem_index="A",
            name="DP 2",
            rating=1150,
            tags="dp",
        ),
        Problem(
            contest_id=3,
            problem_index="A",
            name="DP 3",
            rating=1200,
            tags="dp",
        ),
    ]

    db.add_all(problems)
    db.commit()

    submissions = [
        Submission(
            user_id=user.id,
            contest_id=1,
            problem_index="A",
            problem_name="DP 1",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=1000,
        ),
        Submission(
            user_id=user.id,
            contest_id=2,
            problem_index="A",
            problem_name="DP 2",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=2000,
        ),
        Submission(
            user_id=user.id,
            contest_id=3,
            problem_index="A",
            problem_name="DP 3",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=3000,
        ),
    ]

    db.add_all(submissions)
    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get(
        "/users/testuser/recommendations?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["recommendations"]
    ) == 2

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()


def test_recommendations_endpoint_invalid_limit():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    user = User(
        handle="testuser",
        rating=1000,
    )

    db.add(user)
    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    response = client.get(
        "/users/testuser/recommendations?limit=0"
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Limit must be between 1 and 50"
    }

    app.dependency_overrides.clear()

    db.close()
    engine.dispose()