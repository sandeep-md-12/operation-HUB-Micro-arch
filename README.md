# Operations Hub — Production Deployment

A production-ready FastAPI microservice platform with automated CI/CD, Docker containerization, Nginx reverse proxy, and AWS integration.

---

## Architecture Overview

```
Internet
    │
    ▼
┌─────────────────────────────────────────────┐
│              AWS EC2 Instance               │
│                                             │
│  ┌──────────┐    ┌──────────────────────┐   │
│  │  Nginx   │───▶│   FastAPI (uvicorn)  │   │
│  │  :80     │    │   rvl_web  :8000     │   │
│  └──────────┘    └──────────┬───────────┘   │
│                             │               │
│              ┌──────────────┼────────────┐  │
│              ▼              ▼            ▼  │
│        ┌──────────┐  ┌──────────┐  ┌──────┐ │
│        │PostgreSQL│  │  Redis   │  │Celery│ │
│        │  :5432   │  │  :6379   │  │Worker│ │
│        └──────────┘  └──────────┘  └──────┘ │
└─────────────────────────────────────────────┘
          │                   │
          ▼                   ▼
    AWS DynamoDB          AWS S3
    (Audit Logs)       (File Storage)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 15 (via SQLAlchemy async) |
| Cache / Queue | Redis 7 |
| Background Tasks | Celery |
| Reverse Proxy | Nginx |
| Containerization | Docker + Docker Compose |
| Cloud | AWS EC2, S3, DynamoDB |
| CI/CD | GitHub Actions |
| Image Registry | Docker Hub |

---

## CI/CD Pipeline

Every code change goes through 3 automated stages:

```
Push / Pull Request to main
         │
         ▼
┌─────────────────────┐
│  JOB 1 — CI Tests   │  ← Runs on every push and PR
│  pytest quality gate│  ← FAILED TESTS BLOCK DEPLOY
└────────┬────────────┘
         │ (merge to main only)
         ▼
┌─────────────────────────────┐
│  JOB 2 — Build & Push Image │  ← Builds multi-stage Docker image
│  → Docker Hub               │  ← Tags: :latest + :sha-<commit>
└────────┬────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  JOB 3 — CD: Deploy to EC2                   │
│  1. SSH into EC2                             │
│  2. Install Docker/Git if needed             │
│  3. Clone repo (first time) or git pull      │
│  4. Write .env from GitHub Secrets           │
│  5. docker pull latest image from Docker Hub │
│  6. docker compose up (prod override)        │
│  7. Health check — curl /health              │
│  8. docker image prune                       │
└──────────────────────────────────────────────┘
```

> **Why pre-build on GitHub Actions and pull on EC2?**
> Building on EC2 is slow (small instances, no layer caching). By building on GitHub's powerful runners with GitHub Actions cache, deployments are **10x faster** and EC2 only needs to pull a ready image.

---

## Branching Strategy (Day 1)

```
main          ← Protected. CI must pass. Only via Pull Request.
  └── feature/your-feature-name   ← All new work done here
  └── fix/bug-description
```

**Workflow:**
1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes and commit
3. Open a Pull Request to `main`
4. CI runs automatically — tests must pass to merge
5. On merge → Docker image is built and pushed → EC2 auto-deploys

---

## Local Development Setup

### Prerequisites
- Docker Desktop
- Python 3.11

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sandeep-md-12/operation-HUB-Micro-arch.git
cd operation-HUB-Micro-arch

# 2. Create your environment file
cp .env.example .env
# Edit .env with your values

# 3. Start all services
docker compose up --build

# 4. API is available at http://localhost/
# 5. Health check: http://localhost/health
```

### Running Tests Locally

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest --tb=short -v
```

---

## GitHub Secrets Setup

Go to your GitHub repo → **Settings → Secrets and variables → Actions** and add:

### EC2 & Deployment
| Secret | Description |
|---|---|
| `EC2_HOST` | EC2 public IP address |
| `EC2_USERNAME` | SSH user (e.g. `ubuntu`) |
| `EC2_SSH_KEY` | Contents of your `.pem` private key |
| `GITHUB_REPO_URL` | `https://github.com/sandeep-md-12/operation-HUB-Micro-arch.git` |

### Docker Hub
| Secret | Description |
|---|---|
| `DOCKERHUB_USERNAME` | `mdsandeepkumar2004` |
| `DOCKERHUB_TOKEN` | Docker Hub access token (from Account → Security) |

### Application
| Secret | Description |
|---|---|
| `DATABASE_URL` | Full PostgreSQL URL |
| `POSTGRES_USER` | DB username |
| `POSTGRES_PASSWORD` | DB password |
| `POSTGRES_DB` | DB name |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | `HS256` |
| `AWS_REGION` | e.g. `ap-south-1` |
| `AWS_ACCESS_KEY_ID` | AWS IAM key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret |
| `S3_BUCKET_NAME` | S3 bucket name |
| `DYNAMODB_TABLE_NAME` | `AuditLogs` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | Gmail address |
| `SMTP_PASSWORD` | Gmail app password |
| `APP_BASE_URL` | `http://<EC2-IP>` |
| `INTERNAL_SERVICE_TOKEN` | Random strong token |

---

## EC2 Deployment (First Time)

The CD pipeline handles everything automatically. The only manual step is:

1. Launch an **Ubuntu 22.04** EC2 instance (t2.micro or larger)
2. Open **Security Group** inbound rules:
   - Port `22` (SSH) — your IP
   - Port `80` (HTTP) — anywhere (`0.0.0.0/0`)
3. Add all GitHub Secrets listed above
4. Push/merge any commit to `main`

The pipeline will SSH in, install Docker, clone the repo, write `.env`, and start all services automatically.

---

## Infrastructure Resilience

All containers run with `restart: unless-stopped`. This means:

- If a container crashes → Docker automatically restarts it
- If EC2 reboots → Docker daemon starts on boot, containers restart automatically
- No manual intervention needed

---

## Key Files

```
.
├── .github/
│   └── workflows/
│       └── ci-cd.yml          ← GitHub Actions pipeline (CI + Build + CD)
├── app/                        ← FastAPI application source
├── nginx/
│   └── default.conf           ← Nginx reverse proxy config
├── tests/                      ← Pytest test suite
├── Dockerfile                  ← Multi-stage Docker build
├── docker-compose.yml          ← All services (dev + prod base)
├── docker-compose.prod.yml     ← Production override (pulls from Docker Hub)
├── requirements.txt
└── .env.example               ← Environment variable template
```

---

## Architectural Decisions

| Decision | Reason |
|---|---|
| Multi-stage Dockerfile | Keeps final image small — build tools not included in runtime |
| Non-root container user | Security best practice — limits blast radius if container is compromised |
| Pre-build image on CI, pull on EC2 | Faster deploys, consistent image, no build failures on small EC2 |
| Nginx in front of FastAPI | Handles WebSockets, large uploads, can add SSL later without changing app |
| `restart: unless-stopped` | Survives EC2 reboots; only stops if you explicitly stop the container |
| GitHub Secrets for all env vars | Zero sensitive data in codebase or EC2 filesystem history |
| Health checks on all services | Containers only start when dependencies are truly ready |
