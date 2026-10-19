from datetime import datetime, timedelta, timezone
import time

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.codeforces_client import CodeforcesClient
from app.models import Rating, Submission, User


def get_user_by_handle(
    db: Session,
    handle: str,
) -> User | None:
    return (
        db.query(User)
        .filter(
            func.lower(User.handle) == handle.lower()
        )
        .first()
    )


def is_user_cache_fresh(
    user: User,
    cache_minutes: int = 30,
) -> bool:
    if user.last_synced_at is None:
        return False

    last_synced_at = user.last_synced_at

    if last_synced_at.tzinfo is None:
        last_synced_at = last_synced_at.replace(
            tzinfo=timezone.utc,
        )

    now = datetime.now(timezone.utc)

    return now - last_synced_at < timedelta(
        minutes=cache_minutes,
    )


def save_user(
    db: Session,
    user_data: dict,
) -> User:
    handle = user_data["handle"]

    user = get_user_by_handle(
        db,
        handle,
    )

    if user is None:
        user = User(
            handle=handle,
        )
        db.add(user)

    user.rating = user_data.get("rating")
    user.max_rating = user_data.get("maxRating")
    user.rank = user_data.get("rank")
    user.max_rank = user_data.get("maxRank")
    user.last_synced_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(user)

    return user


def save_rating_history(
    db: Session,
    user: User,
    rating_data: list[dict],
) -> None:
    existing_contest_ids = {
        contest_id
        for (contest_id,) in (
            db.query(Rating.contest_id)
            .filter(
                Rating.user_id == user.id,
            )
            .all()
        )
    }

    for rating in rating_data:
        contest_id = rating["contestId"]

        if contest_id in existing_contest_ids:
            continue

        db.add(
            Rating(
                user_id=user.id,
                contest_id=contest_id,
                contest_name=rating["contestName"],
                old_rating=rating["oldRating"],
                new_rating=rating["newRating"],
                rank=rating["rank"],
            )
        )

        existing_contest_ids.add(contest_id)

    db.commit()


def save_submissions(
    db: Session,
    user: User,
    submission_data: list[dict],
) -> None:
    existing_submissions = (
        db.query(
            Submission.contest_id,
            Submission.problem_index,
            Submission.submission_time,
            Submission.verdict,
        )
        .filter(
            Submission.user_id == user.id,
        )
        .all()
    )

    existing_keys = {
        (
            contest_id,
            problem_index,
            submission_time,
            verdict,
        )
        for (
            contest_id,
            problem_index,
            submission_time,
            verdict,
        ) in existing_submissions
    }

    new_submissions = []

    for submission in submission_data:
        contest_id = submission.get("contestId")
        problem = submission.get("problem", {})

        problem_index = problem.get("index")
        problem_name = problem.get("name")

        if problem_index is None:
            continue

        submission_time = submission.get(
            "creationTimeSeconds"
        )

        if submission_time is None:
            continue

        verdict = submission.get(
            "verdict",
            "",
        )

        key = (
            contest_id,
            problem_index,
            submission_time,
            verdict,
        )

        if key in existing_keys:
            continue

        new_submissions.append(
            Submission(
                user_id=user.id,
                contest_id=contest_id,
                problem_index=problem_index,
                problem_name=problem_name or "Unknown",
                verdict=verdict,
                programming_language=submission.get(
                    "programmingLanguage",
                    "",
                ),
                submission_time=submission_time,
            )
        )

        existing_keys.add(key)

    db.add_all(new_submissions)
    db.commit()

    print(
        f"Saved {len(new_submissions)} new submissions."
    )


def sync_user_profile(
    db: Session,
    handle: str,
) -> User:
    client = CodeforcesClient()

    try:
        user_data = client.get_user_info(handle)

        return save_user(
            db,
            user_data,
        )

    finally:
        client.close()


def background_sync_user(
    handle: str,
) -> None:
    db = SessionLocal()

    try:
        sync_user(
            db,
            handle,
            force=True,
        )
    finally:
        db.close()


def sync_user(
    db: Session,
    handle: str,
    force: bool = False,
) -> User:
    start = time.perf_counter()

    user = get_user_by_handle(
        db,
        handle,
    )

    if (
        not force
        and user is not None
        and is_user_cache_fresh(user)
    ):
        print(
            f"Cache hit: "
            f"{time.perf_counter() - start:.2f}s"
        )
        return user

    client = CodeforcesClient()

    try:
        step_start = time.perf_counter()

        user_data = client.get_user_info(handle)

        print(
            f"user.info: "
            f"{time.perf_counter() - step_start:.2f}s"
        )

        step_start = time.perf_counter()

        user = save_user(
            db,
            user_data,
        )

        print(
            f"save_user: "
            f"{time.perf_counter() - step_start:.2f}s"
        )

        step_start = time.perf_counter()

        rating_data = client.get_user_rating(handle)

        print(
            f"user.rating: "
            f"{time.perf_counter() - step_start:.2f}s"
        )

        step_start = time.perf_counter()

        save_rating_history(
            db,
            user,
            rating_data,
        )

        print(
            f"save_rating_history: "
            f"{time.perf_counter() - step_start:.2f}s"
        )

        step_start = time.perf_counter()

        submission_data = client.get_user_submissions(
            handle,
        )

        print(
            f"user.status: "
            f"{time.perf_counter() - step_start:.2f}s"
        )

        step_start = time.perf_counter()

        save_submissions(
            db,
            user,
            submission_data,
        )

        print(
            f"save_submissions: "
            f"{time.perf_counter() - step_start:.2f}s"
        )

        print(
            f"Total sync: "
            f"{time.perf_counter() - start:.2f}s"
        )

        return user

    finally:
        client.close()