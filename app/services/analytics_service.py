from collections import Counter

from sqlalchemy.orm import Session

from app.models import Problem, Rating, Submission

def get_rating_history(
    db: Session,
    user_id: int,
) -> list[dict]:
    ratings = (
        db.query(Rating)
        .filter(Rating.user_id == user_id)
        .order_by(Rating.id)
        .all()
    )

    return [
        {
            "contest_id": rating.contest_id,
            "contest_name": rating.contest_name,
            "old_rating": rating.old_rating,
            "new_rating": rating.new_rating,
            "rank": rating.rank,
        }
        for rating in ratings
    ]

def get_solved_problem_count(
    db: Session,
    user_id: int,
) -> int:
    solved_problems = (
        db.query(
            Submission.contest_id,
            Submission.problem_index,
        )
        .filter(
            Submission.user_id == user_id,
            Submission.verdict == "OK",
        )
        .distinct()
        .all()
    )

    return len(solved_problems)

def get_solved_problems_by_difficulty(
    db: Session,
    user_id: int,
) -> dict[int, int]:
    solved_problems = (
        db.query(
            Problem.contest_id,
            Problem.problem_index,
            Problem.rating,
        )
        .join(
            Submission,
            (Submission.contest_id == Problem.contest_id)
            & (
                Submission.problem_index
                == Problem.problem_index
            ),
        )
        .filter(
            Submission.user_id == user_id,
            Submission.verdict == "OK",
            Problem.rating.is_not(None),
        )
        .distinct()
        .all()
    )

    difficulty_counts = Counter(
        rating
        for _, _, rating in solved_problems
    )

    return dict(
        sorted(difficulty_counts.items())
    )

def get_solved_problems_by_tag(
    db: Session,
    user_id: int,
) -> dict[str, int]:
    solved_problems = (
        db.query(
            Problem.contest_id,
            Problem.problem_index,
            Problem.tags,
        )
        .join(
            Submission,
            (Submission.contest_id == Problem.contest_id)
            & (
                Submission.problem_index
                == Problem.problem_index
            ),
        )
        .filter(
            Submission.user_id == user_id,
            Submission.verdict == "OK",
            Problem.tags.is_not(None),
        )
        .distinct()
        .all()
    )

    tag_counts = Counter()

    for _, _, tags in solved_problems:
        for tag in tags.split(","):
            tag = tag.strip()

            if tag:
                tag_counts[tag] += 1

    return dict(
        sorted(
            tag_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )

def get_success_rate_by_tag(
    db: Session,
    user_id: int,
) -> dict[str, float]:
    submissions = (
        db.query(
            Submission.verdict,
            Problem.tags,
        )
        .join(
            Problem,
            (Submission.contest_id == Problem.contest_id)
            & (
                Submission.problem_index
                == Problem.problem_index
            ),
        )
        .filter(
            Submission.user_id == user_id,
            Problem.tags.is_not(None),
        )
        .all()
    )

    total_counts = Counter()
    accepted_counts = Counter()

    for verdict, tags in submissions:
        for tag in tags.split(","):
            tag = tag.strip()

            if not tag:
                continue

            total_counts[tag] += 1

            if verdict == "OK":
                accepted_counts[tag] += 1

    success_rates = {}

    for tag, total in total_counts.items():
        success_rates[tag] = round(
            accepted_counts[tag] / total,
            3,
        )

    return dict(
        sorted(
            success_rates.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )

def get_weak_topics(
    db: Session,
    user_id: int,
    min_submissions: int = 3,
    max_success_rate: float = 0.5,
) -> list[dict]:
    submissions = (
        db.query(
            Submission.verdict,
            Problem.tags,
        )
        .join(
            Problem,
            (Submission.contest_id == Problem.contest_id)
            & (
                Submission.problem_index
                == Problem.problem_index
            ),
        )
        .filter(
            Submission.user_id == user_id,
            Problem.tags.is_not(None),
        )
        .all()
    )

    total_counts = Counter()
    accepted_counts = Counter()

    for verdict, tags in submissions:
        for tag in tags.split(","):
            tag = tag.strip()

            if not tag:
                continue

            total_counts[tag] += 1

            if verdict == "OK":
                accepted_counts[tag] += 1

    weak_topics = []

    for tag, total in total_counts.items():
        if total < min_submissions:
            continue

        success_rate = accepted_counts[tag] / total

        if success_rate < max_success_rate:
            weak_topics.append(
                {
                    "tag": tag,
                    "success_rate": round(
                        success_rate,
                        3,
                    ),
                    "submissions": total,
                }
            )

    weak_topics.sort(
        key=lambda item: item["success_rate"]
    )

    return weak_topics