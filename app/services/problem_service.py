from sqlalchemy.orm import Session

from app.codeforces_client import CodeforcesClient
from app.database import SessionLocal
from app.models import Problem


def save_problemset(
    db: Session,
    problemset_data: dict,
) -> int:
    problems = problemset_data.get(
        "problems",
        [],
    )

    new_problems = []

    for problem_data in problems:
        problem_index = problem_data.get("index")
        problem_name = problem_data.get("name")

        if not problem_index or not problem_name:
            continue

        tags = ",".join(
            problem_data.get("tags", [])
        )

        new_problems.append(
            Problem(
                contest_id=problem_data.get(
                    "contestId"
                ),
                problem_index=problem_index,
                name=problem_name,
                rating=problem_data.get("rating"),
                tags=tags,
            )
        )

    if not new_problems:
        return 0

    db.add_all(new_problems)
    db.commit()

    return len(new_problems)


def sync_problemset_if_empty() -> int:
    db = SessionLocal()

    try:
        existing_count = (
            db.query(Problem)
            .count()
        )

        if existing_count > 0:
            print(
                f"Problemset already initialized: "
                f"{existing_count} problems."
            )
            return existing_count

        print(
            "Problemset is empty. "
            "Downloading Codeforces problemset..."
        )

        client = CodeforcesClient()

        try:
            problemset_data = client.get_problemset()
        finally:
            client.close()

        saved_count = save_problemset(
            db,
            problemset_data,
        )

        print(
            f"Saved {saved_count} problems."
        )

        return saved_count

    finally:
        db.close()


if __name__ == "__main__":
    sync_problemset_if_empty()