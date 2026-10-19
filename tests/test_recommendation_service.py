from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Problem, User, Submission

from app.services.recommendation_service import (
    get_candidate_problems,
    filter_by_weak_tags,
    filter_unsolved_problems,
    score_problem,
    get_recommendations,
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


def test_get_candidate_problems():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    user = User(
        handle="testuser",
        rating=1000,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    db.add_all(
        [
            Problem(
                contest_id=1,
                problem_index="A",
                name="Too Easy",
                rating=900,
                tags="dp",
            ),
            Problem(
                contest_id=2,
                problem_index="A",
                name="Good Problem",
                rating=1100,
                tags="dp",
            ),
            Problem(
                contest_id=3,
                problem_index="A",
                name="Good Problem 2",
                rating=1250,
                tags="graphs",
            ),
            Problem(
                contest_id=4,
                problem_index="A",
                name="Too Hard",
                rating=1400,
                tags="dp",
            ),
        ]
    )

    db.commit()

    candidates = get_candidate_problems(
        db,
        user.id,
    )

    assert len(candidates) == 2

    assert {
        problem.name
        for problem in candidates
    } == {
        "Good Problem",
        "Good Problem 2",
    }

    db.close()
    engine.dispose()


def test_filter_by_weak_tags():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    problems = [
        Problem(
            contest_id=1,
            problem_index="A",
            name="DP Problem",
            rating=1100,
            tags="dp,greedy",
        ),
        Problem(
            contest_id=2,
            problem_index="A",
            name="Graph Problem",
            rating=1100,
            tags="graphs",
        ),
        Problem(
            contest_id=3,
            problem_index="A",
            name="Math Problem",
            rating=1100,
            tags="math",
        ),
    ]

    db.add_all(problems)
    db.commit()

    filtered = filter_by_weak_tags(
        problems,
        {"dp"},
    )

    assert len(filtered) == 1
    assert filtered[0].name == "DP Problem"

    db.close()
    engine.dispose()


def test_filter_unsolved_problems():
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
            name="Already Solved",
            rating=1100,
            tags="dp",
        ),
        Problem(
            contest_id=2,
            problem_index="A",
            name="Not Solved",
            rating=1100,
            tags="dp",
        ),
    ]

    db.add_all(problems)
    db.commit()

    db.add(
        Submission(
            user_id=user.id,
            contest_id=1,
            problem_index="A",
            problem_name="Already Solved",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1000,
        )
    )

    db.commit()

    from app.services.recommendation_service import (
        get_solved_problem_keys,
        filter_unsolved_problems,
    )

    solved_keys = get_solved_problem_keys(
        db,
        user.id,
    )

    filtered = filter_unsolved_problems(
        problems,
        solved_keys,
    )

    assert len(filtered) == 1
    assert filtered[0].name == "Not Solved"

    db.close()
    engine.dispose()


def test_score_problem_prefers_weak_tags():
    engine, SessionLocal = create_test_database()
    db = SessionLocal()

    problem_one = Problem(
        contest_id=1,
        problem_index="A",
        name="One Weak Tag",
        rating=1200,
        tags="dp",
    )

    problem_two = Problem(
        contest_id=2,
        problem_index="A",
        name="Two Weak Tags",
        rating=1200,
        tags="dp,greedy",
    )

    weak_tags = {"dp", "greedy"}

    score_one = score_problem(
        problem_one,
        1000,
        weak_tags,
    )

    score_two = score_problem(
        problem_two,
        1000,
        weak_tags,
    )

    assert score_two > score_one

    db.close()
    engine.dispose()


def test_get_recommendations():
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
            name="Weak Topic Problem",
            rating=1200,
            tags="dp",
        ),
        Problem(
            contest_id=2,
            problem_index="A",
            name="Another Weak Problem",
            rating=1150,
            tags="dp",
        ),
        Problem(
            contest_id=3,
            problem_index="A",
            name="Other Problem",
            rating=1200,
            tags="graphs",
        ),
        Problem(
            contest_id=4,
            problem_index="A",
            name="Another DP Attempt",
            rating=1100,
            tags="dp",
        ),
    ]

    db.add_all(problems)
    db.commit()

    db.add(
        Submission(
            user_id=user.id,
            contest_id=1,
            problem_index="A",
            problem_name="Weak Topic Problem",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1000,
        )
    )

    db.add(
        Submission(
            user_id=user.id,
            contest_id=2,
            problem_index="A",
            problem_name="Another Weak Problem",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=2000,
        )
    )

    db.add(
        Submission(
            user_id=user.id,
            contest_id=3,
            problem_index="A",
            problem_name="Other Problem",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=3000,
        )
    )

    db.add(
        Submission(
            user_id=user.id,
            contest_id=4,
            problem_index="A",
            problem_name="Another DP Attempt",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=2500,
        )
    )

    db.commit()

    recommendations = get_recommendations(
        db,
        user.id,
        limit=10,
    )

    assert len(recommendations) == 2

    recommendation_names = {
        recommendation["name"]
        for recommendation in recommendations
    }

    assert recommendation_names == {
        "Another Weak Problem",
        "Another DP Attempt",
    }

    for recommendation in recommendations:
        assert recommendation["rating"] in {
            1100,
            1150,
        }

        assert "dp" in recommendation["tags"]
        assert recommendation["score"] > 0
        assert "weak" in recommendation["reason"].lower()

    assert "Weak Topic Problem" not in recommendation_names
    assert "Other Problem" not in recommendation_names

    db.close()
    engine.dispose()

def test_get_recommendations_respects_limit():
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
            name="Solved Problem",
            rating=1200,
            tags="dp",
        ),
        Problem(
            contest_id=2,
            problem_index="A",
            name="Recommendation One",
            rating=1150,
            tags="dp",
        ),
        Problem(
            contest_id=3,
            problem_index="A",
            name="Recommendation Two",
            rating=1100,
            tags="dp",
        ),
        Problem(
            contest_id=4,
            problem_index="A",
            name="Failed Attempt",
            rating=1050,
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
            problem_name="Solved Problem",
            verdict="OK",
            programming_language="GNU C++17",
            submission_time=1000,
        ),
        Submission(
            user_id=user.id,
            contest_id=4,
            problem_index="A",
            problem_name="Failed Attempt",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=2000,
        ),
        Submission(
            user_id=user.id,
            contest_id=4,
            problem_index="A",
            problem_name="Failed Attempt",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=3000,
        ),
        Submission(
            user_id=user.id,
            contest_id=4,
            problem_index="A",
            problem_name="Failed Attempt",
            verdict="WRONG_ANSWER",
            programming_language="GNU C++17",
            submission_time=4000,
        ),
    ]

    db.add_all(submissions)
    db.commit()

    recommendations = get_recommendations(
        db,
        user.id,
        limit=1,
    )

    assert len(recommendations) == 1

    assert recommendations[0]["name"] in {
        "Recommendation One",
        "Recommendation Two",
    }

    db.close()
    engine.dispose()