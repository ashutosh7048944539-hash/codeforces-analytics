# Codeforces Analytics & Practice Recommender

A full-stack dashboard that analyzes a Codeforces user's performance and recommends unsolved problems based on their weak topics and current rating. Every recommendation comes with a plain-English explanation of why it was picked.

**Live demo:** https://codeforces-analytics-2g9d.onrender.com
(If the app has been idle, the first request may take a while to wake up.)

## Screenshots

Dashboard: summary cards and rating history.

![Dashboard with rating history](docs/dashboard.png)

Weak topics, with the success rate and number of submissions behind each one.

![Weak topics](docs/weak-topics.png)

Recommended problems, each with its tags, difficulty, number of matched weak topics, and score.

![Recommended problems](docs/recommendations.png)

## At a glance

| | |
|---|---|
| Tests | 44 passing, run in CI against a real PostgreSQL |
| Recommendation quality | [TODO: backtest result, e.g. "matches X% of next-solved tags"] |

## Features

- Profile sync from the official Codeforces API (rating, rank, max rating, max rank)
- Rating history chart
- Solved problems by difficulty and by topic/tag
- Success rate per topic and weak-topic detection
- Personalized problem recommendations with explanations
- Recommendation difficulty that adapts to the user's current rating
- PostgreSQL persistence, Alembic migrations, Docker, pytest, GitHub Actions CI
- Lightweight usage/campaign analytics for tracking analysis starts and traffic sources

## Quick start (Docker)

```bash
git clone https://github.com/ashutosh7048944539-hash/codeforces-analytics.git
cd codeforces-analytics
docker compose up -d
```

Open http://localhost:8000. On startup the container runs Alembic migrations, loads the Codeforces problemset if the database has none, and then starts the app.

## How it works

```mermaid
flowchart TD
    CF[Codeforces API] --> API[FastAPI backend]
    API --> DB[(PostgreSQL)]
    API --> AN[Analytics service]
    AN --> WT[Weak-topic detection]
    DB --> REC[Recommendation engine]
    WT --> REC
    REC --> UI[Jinja2 + Chart.js dashboard]
```

1. The backend fetches a user's profile, rating history, and submissions from the Codeforces API (rate-limited) and stores them in PostgreSQL.
2. The analytics service computes solve counts and success rates by difficulty and by topic, and flags weak topics.
3. The recommendation engine combines the weak topics with the stored problemset and returns ranked problems.
4. The dashboard renders everything with Jinja2 templates and Chart.js.

## Recommendation logic

The engine:

1. Reads the user's current rating.
2. Finds topics where the user's success rate is low.
3. Selects problems rated between `current rating + 100` and `current rating + 300`. If no problem exists in that range, the system falls back to the highest-rated available problems within 200 rating points of the maximum problem rating in the database.
4. Keeps problems that match weak topics and removes problems the user has already solved.
5. Scores what remains and returns the top results with an explanation for each.

**Score** (higher is better):

```text
score = 0.5 * weak_topic_coverage
      + 0.3 * weakness_severity
      + 0.2 * difficulty_suitability
```

- `weak_topic_coverage`: the number of the problem's tags that are weak topics, divided by 5 and capped at 1.
- `weakness_severity`: the average of (1 - success rate) over the problem's matching weak topics.
- `difficulty_suitability`: 1 - |problem rating - (current rating + 200)| / 200, floored at 0.

## API

| Endpoint | Description |
|---|---|
| `GET /health`, `GET /healthz` | Health checks |
| `GET /users/{handle}/analytics` | Ratings, ranks, solved count, difficulty and topic distributions, topic success rates, weak topics |
| `GET /users/{handle}/rating-history` | Contest rating history |
| `GET /users/{handle}/recommendations?limit=10` | Ranked practice problems with explanations |

Example:

```text
GET /users/ashutoshthelearner/recommendations?limit=10
```

## Database

```text
User
  |
  +---- Rating
  |
  +---- Submission

Problem
```

| Table | Stores |
|---|---|
| `User` | Codeforces profile information |
| `Rating` | Contest rating changes |
| `Submission` | Submitted solutions and their verdicts |
| `Problem` | The Codeforces problemset used for recommendations |
| `AnalyticsEvent` | Usage and campaign events such as analysis starts and traffic sources |

Schema changes are managed with Alembic.

## Design decisions

- **Persist everything in PostgreSQL.** Submissions are stored so repeat visits do not re-download a user's whole history, and the recommender can query solved problems directly.
- **Routers and services are separate.** Routers handle HTTP only; analytics, problems, users, and recommendations live in service modules, which keeps them testable without a web server.
- **Rate limiting in the Codeforces client.** Requests are throttled to respect the official API limits, and this behavior is covered by tests.
- **Explainable recommendations.** Each result carries a human-readable reason, so users can see why a problem was suggested.
- **Caching and synchronization.** User data is reused while the cache is fresh, but a fresh profile is re-synchronized if its rating or submission analytics data is missing. This prevents partially populated users from producing empty analytics or recommendations.

## Testing and CI

```bash
pytest
```

The suite has 44 tests covering the service layer, API, Codeforces client, rate limiting, recommendations, caching, analytics, health endpoints, and PostgreSQL integration.

GitHub Actions starts PostgreSQL, installs dependencies, runs Alembic migrations, and runs the full suite on every push to `main` and every pull request targeting `main`.

## Run locally (without Docker for the app)

Requires Python and Docker (for PostgreSQL).

```bash
# 1. Virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .\.venv\Scripts\Activate.ps1

# 2. Dependencies
pip install -r requirements.txt

# 3. Environment: copy .env.example to .env, or create .env with:
#    DATABASE_URL=postgresql+psycopg://cf_user:cf_password@localhost:5432/codeforces

# 4. PostgreSQL
docker compose up -d

# 5. Migrations and problemset
alembic upgrade head
python -m app.services.problem_service

# 6. Run the app
uvicorn app.main:app --reload
```

Open http://localhost:8000.

## Project structure

```text
codeforces-analytics/
├── app/
│   ├── routers/             # analytics.py, health.py, recommendations.py
│   ├── services/            # analytics, analytics events, problem, recommendation, user services
│   ├── codeforces_client.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── alembic/versions/       # database migrations
├── templates/index.html
├── tests/
├── .github/workflows/      # CI
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
└── requirements.txt
```

## Deployment

Deployed on Render as a Docker web service with a Render PostgreSQL database. The container runs Alembic migrations, initializes the problemset, then starts FastAPI on the port provided by the platform.

## Known limitations

- The problemset is downloaded only when the database has no problems, so problems from newer contests are not added automatically. 
- Codeforces API responses are not persistently cached; user synchronization is skipped while the stored user data is fresh and complete.
- No authentication or per-user accounts.

## Roadmap

- Scheduled problemset refresh
- Caching of Codeforces API responses
- Time-based progress tracking
- Recommendation feedback ("solved" / "too hard") to tune the scoring
- Background jobs for syncing
- More advanced recommendation models

## License

This project is intended as a personal portfolio and learning project.
