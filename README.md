# CodePulse AI

A full-stack competitive programming insights platform that aggregates your coding profiles across **LeetCode**, **Codeforces**, **CodeChef**, and **HackerRank** — then uses **Google Gemini AI** to generate personalized insights, a 90-day improvement roadmap, and an AI mentor chat.

## Features

- **Multi-Platform Profile Aggregation** — Link your competitive coding accounts and scrape stats (problems solved, difficulty breakdown, topic coverage, contest ratings, submission heatmaps)
- **AI-Powered Insights** — Gemini analyzes your cross-platform data to identify strengths, weaknesses, career recommendations, and an overall score
- **AI Mentor Chat** — Context-aware chat that knows your actual profile data, topics, and scores
- **OAuth Authentication** — Sign in with Google or GitHub (or email/password)
- **Recruitment Module** — Companies can create assessments, post jobs, and AI-match candidates
- **Responsive UI** — Mobile-first design with dark theme, bottom navigation, and adaptive charts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 3 |
| Backend | Python FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL (Neon cloud or local via Docker) |
| AI | Google Gemini 2.0 Flash |
| Auth | JWT (access + refresh tokens), Google & GitHub OAuth 2.0 |
| Deployment | Docker Compose (backend), Vercel (frontend) |

## Project Structure

```
codepulse-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Pydantic settings
│   │   ├── database.py             # Async SQLAlchemy engine
│   │   ├── models/                 # ORM models (user, profile, insight, chat, company, etc.)
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── api/
│   │   │   ├── deps.py             # Auth dependency (get_current_user)
│   │   │   └── v1/                 # API routes (auth, profiles, insights, chat, etc.)
│   │   ├── services/               # Business logic
│   │   │   ├── scraper/            # Platform scrapers (LeetCode, Codeforces, CodeChef, HackerRank)
│   │   │   └── ai/                 # Gemini client, insight generator, chat engine
│   │   └── core/                   # Security (JWT, bcrypt), OAuth helpers, exceptions
│   ├── alembic/                    # Database migrations
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Landing page
│   │   │   ├── (auth)/             # Login, Register, OAuth callback
│   │   │   └── dashboard/          # Overview, Insights, Chat, Settings
│   │   ├── components/
│   │   │   ├── ui/                 # Button, Input, Card, ProgressBar, Modal
│   │   │   ├── layout/             # Navbar, Sidebar, Footer
│   │   │   ├── dashboard/          # DifficultyChart, TopicChart, TopicRadar, ActivityHeatmap
│   │   │   ├── insights/           # InsightCardGrid, TopicCoverage, StrengthRadar, Roadmap
│   │   │   └── chat/               # ChatWindow, ChatMessage (markdown), ChatInput
│   │   └── lib/
│   │       ├── api-client.ts       # Fetch wrapper with auto token refresh
│   │       ├── auth.ts             # Token storage
│   │       ├── hooks/              # useAuth, useProfile, useInsights, useChat
│   │       └── types/              # TypeScript interfaces
│   ├── tailwind.config.ts
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (for backend + local PostgreSQL)
- **Node.js 18+** and **pnpm** (for frontend)
- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/apikey)
- **Google OAuth credentials** — [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
- **GitHub OAuth App** — [GitHub Developer Settings](https://github.com/settings/developers)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/codepulse-ai.git
cd codepulse-ai
```

### 2. Backend Setup

```bash
cd backend

# Create environment file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/leetcode_ai
SECRET_KEY=your-random-secret-key
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
FRONTEND_URL=http://localhost:3000
```

> To use a cloud database (e.g., Neon), replace `DATABASE_URL` with your connection string. Make sure it starts with `postgresql+asyncpg://` and includes `?ssl=require`.

Start the backend:

```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`. Tables are auto-created on startup.

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start dev server
pnpm dev
```

The app will be available at `http://localhost:3000`.

### 4. OAuth Configuration

**Google OAuth:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create an OAuth 2.0 Client ID (Web application)
3. Add authorized redirect URI: `http://localhost:8000/api/v1/auth/oauth/google/callback`
4. Copy Client ID and Secret to `.env`

**GitHub OAuth:**
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Create a new OAuth App
3. Set Homepage URL: `http://localhost:3000`
4. Set Authorization callback URL: `http://localhost:8000/api/v1/auth/oauth/github/callback`
5. Copy Client ID and Secret to `.env`

## Usage

1. **Register/Login** — Create an account or sign in with Google/GitHub
2. **Link Platforms** — Go to Settings and connect your LeetCode/Codeforces/CodeChef/HackerRank username
3. **Sync Data** — Click "Sync Data" on the dashboard to scrape your profiles
4. **View Dashboard** — See difficulty breakdown, topic charts, skill radar, and activity heatmap
5. **Generate Insights** — Go to AI Insights and click "Generate Insights" for Gemini-powered analysis
6. **Chat with Mentor** — Open AI Mentor for personalized advice based on your actual coding data

## API Endpoints

All endpoints are under `/api/v1`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register with email/password |
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user |
| GET | `/auth/oauth/google` | Initiate Google OAuth |
| GET | `/auth/oauth/github` | Initiate GitHub OAuth |
| POST | `/profiles/link` | Link a coding platform |
| DELETE | `/profiles/{id}` | Unlink a platform |
| POST | `/profiles/scrape` | Scrape all linked platforms |
| GET | `/profiles` | Get profiles + latest snapshots |
| POST | `/insights/generate` | Generate AI insights |
| GET | `/insights/latest` | Get latest insight report |
| POST | `/chat/sessions` | Create chat session |
| GET | `/chat/sessions` | List chat sessions |
| POST | `/chat/sessions/{id}/messages` | Send message, get AI response |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (must use `postgresql+asyncpg://`) |
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GITHUB_CLIENT_ID` | GitHub OAuth app client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth app client secret |
| `FRONTEND_URL` | Frontend URL for OAuth redirects (default: `http://localhost:3000`) |

## License

MIT
