# Codeforces Analytics & Practice Recommender

A full-stack analytics dashboard that analyzes a Codeforces user's competitive programming performance and recommends unsolved problems based on their weak topics and current rating.

## Live Demo

https://codeforces-analytics-2g9d.onrender.com

## Features

- Codeforces user profile synchronization
- Current and maximum rating
- Current and maximum rank
- Rating history visualization
- Total solved problem count
- Problems solved by difficulty
- Problems solved by topic/tag
- Success rate by topic
- Weak-topic detection
- Personalized problem recommendations
- Recommendation explanations
- Dynamic recommendation difficulty based on current rating
- PostgreSQL persistence
- Alembic database migrations
- Dockerized application
- Automated testing with pytest
- GitHub Actions CI
- Automatic Codeforces problemset initialization

## How It Works

The application follows this flow:

```text
Codeforces API
      |
      v
FastAPI Backend
      |
      +------------------+
      |                  |
      v                  v
PostgreSQL          Analytics
      |                  |
      |                  v
      |             Weak Topics
      |                  |
      +---------> Recommendation Engine
                         |
                         v
                  Personalized Problems
                         |
                         v
                  Jinja2 + Chart.js
                         |
                         v
                    Web Dashboard


## Recommendation Logic

The recommendation engine:

1. Gets the user's current Codeforces rating.
2. Identifies topics where the user's success rate is low.
3. Finds problems around the user's target difficulty range.
4. Keeps problems matching the user's weak topics.
5. Removes already solved problems.
6. Scores the remaining problems using:
   - weak-topic coverage
   - weakness severity
   - difficulty suitability
7. Returns the highest-scoring problems.
8. Generates a human-readable explanation for each recommendation.

The target difficulty is centered approximately around:

```text
current rating + 200


## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

### Frontend

- Jinja2
- HTML
- JavaScript
- Chart.js

### Infrastructure

- Docker
- Docker Compose
- Render
- GitHub Actions

### Testing

- pytest
- FastAPI TestClient
- PostgreSQL integration tests


## Project Structure

```text
codeforces-analytics/
│
├── app/
│   ├── routers/
│   │   ├── analytics.py
│   │   ├── health.py
│   │   └── recommendations.py
│   │
│   ├── services/
│   │   ├── analytics_service.py
│   │   ├── problem_service.py
│   │   ├── recommendation_service.py
│   │   └── user_service.py
│   │
│   ├── codeforces_client.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
│
├── alembic/
│   └── versions/
│
├── templates/
│   └── index.html
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md##



Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/ashutosh7048944539-hash/codeforces-analytics.git
cd codeforces-analytics


```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://cf_user:cf_password@localhost:5432/codeforces
```

### 5. Start PostgreSQL

```powershell
docker compose up -d
```

### 6. Run migrations

```powershell
alembic upgrade head
```

### 7. Initialize the Codeforces problemset

```powershell
python -m app.services.problem_service
```

The problemset is downloaded only when the database does not already contain problems.

### 8. Start the application

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000
```

## Running with Docker

Build the application image:

```powershell
docker build -t codeforces-analytics .
```

Start the complete application:

```powershell
docker compose up -d
```

The application will be available at:

```text
http://localhost:8000
```

The Docker startup process:

1. Runs Alembic migrations.
2. Initializes the Codeforces problemset if necessary.
3. Starts the FastAPI application.


## API Endpoints

### Health

```text
GET /health
GET /healthz
```

### User Analytics

```text
GET /users/{handle}/analytics
```

Returns:

- current rating
- maximum rating
- current rank
- maximum rank
- solved count
- difficulty distribution
- topic distribution
- topic success rates
- weak topics

### Rating History

```text
GET /users/{handle}/rating-history
```

Returns the user's contest rating history.

### Recommendations

```text
GET /users/{handle}/recommendations
```

Optional parameter:

```text
?limit=10
```

Example:

```text
GET /users/ashutoshthelearner/recommendations?limit=10
```

## Testing

Run the complete test suite:

```powershell
pytest
```

Current test status:

```text
41 passed
```

The test suite includes:

- service-layer tests
- API tests
- Codeforces client tests
- rate-limit tests
- PostgreSQL integration tests
- recommendation tests
- health endpoint tests


## CI

GitHub Actions automatically:

1. Starts PostgreSQL.
2. Installs Python dependencies.
3. Runs Alembic migrations.
4. Runs the complete pytest suite.

Every push to `main` and every pull request targeting `main` is tested.

## Database

The application uses PostgreSQL with SQLAlchemy.

Main entities:

```text
User
  |
  +---- Rating
  |
  +---- Submission

Problem
```

### User

Stores Codeforces profile information.

### Rating

Stores contest rating changes.

### Submission

Stores submitted solutions and their verdicts.

### Problem

Stores the Codeforces problemset used by the recommendation engine.

Alembic manages database schema migrations. 


## Deployment

The application is deployed using:

- Render Web Service
- Render PostgreSQL
- Docker

The production container runs:

```text
Alembic migrations
        ↓
Problemset initialization
        ↓
FastAPI
```

The service listens on the port provided by the deployment platform.

## Engineering Highlights

This project demonstrates:

- REST API development with FastAPI
- Relational database design
- SQLAlchemy ORM
- Database migrations
- External API integration
- API rate limiting
- Data synchronization
- Analytics aggregation
- Recommendation algorithms
- Docker containerization
- CI/CD
- PostgreSQL integration testing
- Production deployment

## Future Improvements

Possible extensions include:

- More advanced recommendation scoring
- Contest performance analysis
- Rating prediction
- Time-based progress tracking
- Personalized practice plans
- Recommendation feedback and learning
- More detailed problem difficulty analysis
- Caching Codeforces API responses
- Redis-based background jobs
- Authentication and multiple user accounts

## License

This project is intended as a personal portfolio and learning project.