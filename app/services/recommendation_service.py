from sqlalchemy.orm import Session
from app.services.analytics_service import get_weak_topics
from app.models import User, Problem, Submission


def get_user_rating(
    db: Session,
    user_id: int,
) -> int:
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise ValueError("User not found")

    if user.rating is None:
        raise ValueError("User rating is not available")

    return user.rating

def get_candidate_problems(
    db: Session,
    user_id: int,
) -> list:
    user_rating = get_user_rating(
        db,
        user_id,
    )

    minimum_rating = user_rating + 100
    maximum_rating = user_rating + 300

    problems = (
        db.query(Problem)
        .filter(
            Problem.rating.is_not(None),
            Problem.rating >= minimum_rating,
            Problem.rating <= maximum_rating,
        )
        .all()
    )

    return problems

def get_weak_tags(
    db: Session,
    user_id: int,
) -> set[str]:
    weak_topics = get_weak_topics(
        db,
        user_id,
    )

    return {
        topic["tag"]
        for topic in weak_topics
    }

def filter_by_weak_tags(
    problems: list,
    weak_tags: set[str],
) -> list:
    if not weak_tags:
        return []

    filtered_problems = []

    for problem in problems:
        if not problem.tags:
            continue

        problem_tags = {
            tag.strip()
            for tag in problem.tags.split(",")
            if tag.strip()
        }

        if problem_tags & weak_tags:
            filtered_problems.append(problem)

    return filtered_problems

def get_solved_problem_keys(
    db: Session,
    user_id: int,
) -> set[tuple[int | None, str]]:
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

    return {
        (
            contest_id,
            problem_index,
        )
        for contest_id, problem_index in solved_problems
    }

def filter_unsolved_problems(
    problems: list,
    solved_keys: set[tuple[int | None, str]],
) -> list:
    return [
        problem
        for problem in problems
        if (
            problem.contest_id,
            problem.problem_index,
        ) not in solved_keys
    ]

def score_problem(
    problem,
    user_rating: int,
    weak_tags: set[str],
    weak_topic_rates: dict[str, float] | None = None,
) -> float:
    problem_tags = {
        tag.strip()
        for tag in (problem.tags or "").split(",")
        if tag.strip()
    }

    matching_tags = problem_tags & weak_tags

    if not matching_tags:
        return 0.0

    # More matching weak topics = better coverage.
    # Cap at 5 so problems with many tags do not dominate unfairly.
    coverage_score = min(
        len(matching_tags) / 5,
        1.0,
    )

    # Lower success rate means a stronger weakness.
    if weak_topic_rates:
        weakness_scores = [
            1.0 - weak_topic_rates[tag]
            for tag in matching_tags
            if tag in weak_topic_rates
        ]

        severity_score = (
            sum(weakness_scores) / len(weakness_scores)
            if weakness_scores
            else 0.0
        )
    else:
        severity_score = 1.0

    target_rating = user_rating + 200

    difficulty_distance = abs(
        problem.rating - target_rating
    )

    difficulty_score = max(
        0.0,
        1.0 - difficulty_distance / 200,
    )

    return (
        0.5 * coverage_score
        + 0.3 * severity_score
        + 0.2 * difficulty_score
    )

def rank_problems(
    problems: list,
    user_rating: int,
    weak_tags: set[str],
    weak_topic_rates: dict[str, float] | None = None,
) -> list:
    scored_problems = []

    for problem in problems:
        score = score_problem(
            problem,
            user_rating,
            weak_tags,
            weak_topic_rates,
        )

        scored_problems.append(
            (
                score,
                problem,
            )
        )

    scored_problems.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        problem
        for _, problem in scored_problems
    ]

def get_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10,
) -> list[dict]:
    user_rating = get_user_rating(
        db,
        user_id,
    )

    weak_topics = get_weak_topics(
        db,
        user_id,
    )

    weak_tags = {
        topic["tag"]
        for topic in weak_topics
    }

    weak_topic_rates = {
        topic["tag"]: topic["success_rate"]
        for topic in weak_topics
    }

    candidates = get_candidate_problems(
        db,
        user_id,
    )

    candidates = filter_by_weak_tags(
        candidates,
        weak_tags,
    )

    solved_keys = get_solved_problem_keys(
        db,
        user_id,
    )

    candidates = filter_unsolved_problems(
        candidates,
        solved_keys,
    )

    ranked_problems = rank_problems(
        candidates,
        user_rating,
        weak_tags,
        weak_topic_rates,
    )

    recommendations = []

    for problem in ranked_problems[:limit]:
        score = score_problem(
            problem,
            user_rating,
            weak_tags,
            weak_topic_rates,
        )

        recommendations.append(
            {
                "contest_id": problem.contest_id,
                "problem_index": problem.problem_index,
                "name": problem.name,
                "rating": problem.rating,
                "tags": problem.tags,
                "score": round(score, 3),
                "reason": explain_recommendation(
                    problem,
                    user_rating,
                    weak_tags,
                ),
            }
        )

    return recommendations

def explain_recommendation(
    problem,
    user_rating: int,
    weak_tags: set[str],
) -> str:
    problem_tags = {
        tag.strip()
        for tag in (problem.tags or "").split(",")
        if tag.strip()
    }

    matching_tags = sorted(
        problem_tags & weak_tags
    )

    if matching_tags:
        if len(matching_tags) == 1:
            tags_text = matching_tags[0]

            return (
                f"Recommended because {tags_text} "
                f"is one of your weak topics and this "
                f"problem has a rating of {problem.rating}, "
                f"which is within your target difficulty range."
            )

        tags_text = ", ".join(matching_tags)

        return (
            f"Recommended because this problem matches "
            f"{len(matching_tags)} of your weak topics "
            f"({tags_text}) and has a rating of "
            f"{problem.rating}, which is within your "
            f"target difficulty range."
        )

    return (
        f"Recommended because this problem has a rating "
        f"of {problem.rating}, which is within your "
        f"target difficulty range."
    )