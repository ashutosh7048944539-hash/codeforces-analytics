from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Problem, Rating, Submission, User
from app.services.analytics_service import (
    get_rating_history,
    get_solved_problem_count,
    get_solved_problems_by_difficulty,
    get_solved_problems_by_tag,
    get_success_rate_by_tag,
    get_weak_topics,
)

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


def test_get_rating_history():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(
        Rating(
            user_id=user.id,
            contest_id=100,
            contest_name="Contest 100",
            old_rating=1000,
            new_rating=1100,
            rank=500,
        )
    )

    db.commit()

    result = get_rating_history(
        db,
        user.id,
    )

    assert len(result) == 1
    assert result[0]["contest_id"] == 100
    assert result[0]["old_rating"] == 1000
    assert result[0]["new_rating"] == 1100

    db.close()
    engine.dispose()


def test_save_rating_history():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.user_service import save_rating_history

    rating_data = [
        {
            "contestId": 100,
            "contestName": "Contest 100",
            "oldRating": 1000,
            "newRating": 1100,
            "rank": 500,
        }
    ]

    save_rating_history(
        db,
        user,
        rating_data,
    )

    ratings = db.query(Rating).all()

    assert len(ratings) == 1
    assert ratings[0].contest_id == 100
    assert ratings[0].new_rating == 1100

    db.close()
    engine.dispose()


def test_save_rating_history_avoids_duplicates():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.user_service import save_rating_history

    rating_data = [
        {
            "contestId": 100,
            "contestName": "Contest 100",
            "oldRating": 1000,
            "newRating": 1100,
            "rank": 500,
        }
    ]

    save_rating_history(
        db,
        user,
        rating_data,
    )

    save_rating_history(
        db,
        user,
        rating_data,
    )

    ratings = db.query(Rating).all()

    assert len(ratings) == 1

    db.close()
    engine.dispose()


def test_get_solved_problem_count():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    submissions = [
        Submission(
            user_id=user.id,
            contest_id=100,
            problem_index="A",
            problem_name="Problem A",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1000,
        ),
        Submission(
            user_id=user.id,
            contest_id=100,
            problem_index="A",
            problem_name="Problem A",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1100,
        ),
        Submission(
            user_id=user.id,
            contest_id=100,
            problem_index="B",
            problem_name="Problem B",
            verdict="WA",
            programming_language="GNU C++17",
            submission_time=1200,
        ),
        Submission(
            user_id=user.id,
            contest_id=101,
            problem_index="A",
            problem_name="Problem C",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1300,
        ),
    ]

    db.add_all(submissions)
    db.commit()

    result = get_solved_problem_count(
        db,
        user.id,
    )

    assert result == 2

    db.close()
    engine.dispose()

def test_get_solved_problems_by_difficulty():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add_all(
        [
            Problem(
                contest_id=100,
                problem_index="A",
                name="Easy Problem",
                rating=800,
                tags="implementation",
            ),
            Problem(
                contest_id=100,
                problem_index="B",
                name="Medium Problem",
                rating=1200,
                tags="dp",
            ),
            Problem(
                contest_id=101,
                problem_index="A",
                name="Another Easy Problem",
                rating=800,
                tags="greedy",
            ),
        ]
    )

    db.commit()

    db.add_all(
        [
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="Easy Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1000,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Medium Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1100,
            ),
            Submission(
                user_id=user.id,
                contest_id=101,
                problem_index="A",
                problem_name="Another Easy Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1200,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Medium Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1300,
            ),
        ]
    )

    db.commit()

    result = get_solved_problems_by_difficulty(
        db,
        user.id,
    )

    assert result == {
        800: 2,
        1200: 1,
    }

    db.close()
    engine.dispose()

def test_get_solved_problems_by_tag():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add_all(
        [
            Problem(
                contest_id=100,
                problem_index="A",
                name="Problem A",
                rating=800,
                tags="implementation,greedy",
            ),
            Problem(
                contest_id=100,
                problem_index="B",
                name="Problem B",
                rating=1200,
                tags="dp,greedy",
            ),
            Problem(
                contest_id=101,
                problem_index="A",
                name="Problem C",
                rating=1000,
                tags="implementation,math",
            ),
        ]
    )

    db.commit()

    db.add_all(
        [
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="Problem A",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1000,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Problem B",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1100,
            ),
            Submission(
                user_id=user.id,
                contest_id=101,
                problem_index="A",
                problem_name="Problem C",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1200,
            ),
            # Duplicate accepted submission.
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="Problem A",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1300,
            ),
        ]
    )

    db.commit()

    result = get_solved_problems_by_tag(
        db,
        user.id,
    )

    assert result == {
        "greedy": 2,
        "implementation": 2,
        "dp": 1,
        "math": 1,
    }

    db.close()
    engine.dispose()

def test_get_success_rate_by_tag():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add_all(
        [
            Problem(
                contest_id=100,
                problem_index="A",
                name="Problem A",
                rating=800,
                tags="greedy,implementation",
            ),
            Problem(
                contest_id=100,
                problem_index="B",
                name="Problem B",
                rating=1200,
                tags="dp,greedy",
            ),
        ]
    )

    db.commit()

    db.add_all(
        [
            # greedy + implementation -> OK
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="Problem A",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1000,
            ),
            # greedy + implementation -> WA
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="Problem A",
                verdict="WA",
                programming_language="GNU C++17",
                submission_time=1100,
            ),
            # dp + greedy -> OK
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Problem B",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1200,
            ),
            # dp + greedy -> WA
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Problem B",
                verdict="WA",
                programming_language="GNU C++17",
                submission_time=1300,
            ),
        ]
    )

    db.commit()

    result = get_success_rate_by_tag(
        db,
        user.id,
    )

    assert result == {
        "dp": 0.5,
        "greedy": 0.5,
        "implementation": 0.5,
    }

    db.close()
    engine.dispose()

def test_get_weak_topics():
    engine, SessionLocal = create_test_database()

    db = SessionLocal()

    user = User(handle="testuser")
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add_all(
        [
            Problem(
                contest_id=100,
                problem_index="A",
                name="DP Problem",
                rating=1200,
                tags="dp",
            ),
            Problem(
                contest_id=100,
                problem_index="B",
                name="Greedy Problem",
                rating=1000,
                tags="greedy",
            ),
        ]
    )

    db.commit()

    db.add_all(
        [
            # DP: 1 OK + 3 WA = 25%
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="DP Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1000,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="DP Problem",
                verdict="WA",
                programming_language="GNU C++17",
                submission_time=1100,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="DP Problem",
                verdict="WA",
                programming_language="GNU C++17",
                submission_time=1200,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="A",
                problem_name="DP Problem",
                verdict="WA",
                programming_language="GNU C++17",
                submission_time=1300,
            ),
            # Greedy: 3 OK = 100%
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Greedy Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1400,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Greedy Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1500,
            ),
            Submission(
                user_id=user.id,
                contest_id=100,
                problem_index="B",
                problem_name="Greedy Problem",
                verdict="OK",
                programming_language="GNU C++17",
                submission_time=1600,
            ),
        ]
    )

    db.commit()

    result = get_weak_topics(
        db,
        user.id,
    )

    assert result == [
        {
            "tag": "dp",
            "success_rate": 0.25,
            "submissions": 4,
        }
    ]

    db.close()
    engine.dispose()