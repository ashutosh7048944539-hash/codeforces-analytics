# Codeforces Analytics & Practice Recommender

A full-stack dashboard that analyzes a Codeforces user's performance and recommends unsolved problems based on their weak topics and current rating. Every recommendation comes with a plain-English explanation of why it was picked.

**Live demo:** https://codeforces-analytics-2g9d.onrender.com
(If the app has been idle, the first request may take a while to wake up.)

[TODO: add a screenshot or GIF of the dashboard here, e.g. `![Dashboard](docs/dashboard.png)`]

## At a glance

| | |
|---|---|
| Tests | 41 passing, run in CI against a real PostgreSQL |
| Real users | [TODO: N students/users so far] |
| Recommendation quality | [TODO: backtest result, e.g. "matches X% of next-solved tags"] |
| First sync time | [TODO: e.g. "N submissions in X s"] |

## Features

- Profile sync from the official Codeforces API (rating, rank, max rating, max rank)
- Rating history chart
- Solved problems by difficulty and by topic/tag
- Success rate per topic and weak-topic detection
- Personalized problem recommendations with explanations
- Recommendation difficulty that adapts to the user's current rating
- PostgreSQL persistence, Alembic migrations, Docker, pytest, GitHub Actions CI

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
3. Selects problems around the target difficulty, centered at roughly `current rating + 200`.
4. Keeps problems that match weak topics and removes problems the user has already solved.
5. Scores what remains and returns the top results with an explanation for each.

**Score** (higher is better):

```text
score = [TODO: w1] * weak_topic_coverage
      + [TODO: w2] * weakness_severity
      + [TODO: w3] * difficulty_suitability
```

- `weak_topic_coverage`: [TODO: define, e.g. fraction of the problem's tags that are weak topics]
- `weakness_severity`: [TODO: define, e.g. 1 - success rate of the weakest matching tag]
- `difficulty_suitability`: [TODO: define, e.g. closeness of the problem's rating to the target]
- A topic counts as weak when [TODO: exact rule, including any minimum number of attempts].

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
| User | Codeforces profile information |
| Rating | Contest rating changes |
| Submission | Submitted solutions and their verdicts |
| Problem | The Codeforces problemset used for recommendations |

Schema changes are managed with Alembic.

## Design decisions

- **Persist everything in PostgreSQL.** Submissions are stored so repeat visits do not re-download a user's whole history, and the recommender can query solved problems directly.
- **Routers and services are separate.** Routers handle HTTP only; analytics, problems, users, and recommendations live in service modules, which keeps them testable without a web server.
- **Rate limiting in the Codeforces client.** Requests are throttled to respect the official API limits, and this behavior is covered by tests.
- **Explainable recommendations.** Each result carries a human-readable reason, so users can see why a problem was suggested.
- [TODO: add 1-2 decisions with the tradeoff, e.g. why this scoring approach, why this weak-topic rule]

## Testing and CI

```bash
pytest
```

The suite has 41 tests: service layer, API, Codeforces client, rate limiting, recommendations, health endpoints, and PostgreSQL integration tests.

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
│   ├── routers/            # analytics.py, health.py, recommendations.py
│   ├── services/           # analytics, problem, recommendation, user services
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

- The problemset is downloaded only when the database has no problems, so problems from newer contests are not added automatically. [TODO: remove this line once a refresh job exists]
- Codeforces API responses are not cached yet; each sync calls the API directly.
- No authentication or per-user accounts.

## Roadmap

- Scheduled problemset refresh
- Caching of Codeforces API responses
- Time-based progress tracking
- Recommendation feedback ("solved" / "too hard") to tune the scoring
- Background jobs for syncing

## License

This project is intended as a personal portfolio and learning project.
