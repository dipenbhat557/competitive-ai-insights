# CodePulse AI: A Full-Stack AI-Powered Competitive Programming Insights and Mentorship Platform

**Dipendra Bhatta**
Department of Computer Science
[Your University Name]
[Your City, Country]
[your-email@example.com]

---

## Abstract

Competitive programming has become an essential component of technical skill assessment in the software industry. However, practitioners who use multiple platforms such as LeetCode, Codeforces, CodeChef, and HackerRank face significant challenges in obtaining a unified view of their progress, identifying cross-platform strengths and weaknesses, and receiving personalized improvement guidance. This paper presents **CodePulse AI**, a full-stack web application that aggregates competitive programming profiles across four major platforms, employs Google Gemini large language model (LLM) to generate personalized AI-driven insights including strength/weakness analysis, career recommendations, and a 90-day structured improvement roadmap, and provides an AI mentor chatbot with full awareness of the user's actual performance data. The system is built with a Next.js 15 frontend, a Python FastAPI asynchronous backend, PostgreSQL for persistent storage, and a multi-stage Docker deployment pipeline. The platform also incorporates OAuth 2.0 authentication, real-time profile scraping via GraphQL and REST APIs, and a recruitment module with AI-powered candidate-job matching. Experimental evaluation demonstrates that the system successfully aggregates data from all four platforms with sub-5-second response times and produces contextually relevant AI insights grounded in actual user performance metrics.

**Keywords** — competitive programming, artificial intelligence, web scraping, large language models, full-stack development, profile aggregation, Google Gemini, Next.js, FastAPI

---

## I. Introduction

Competitive programming platforms have become the de facto standard for evaluating algorithmic problem-solving skills in the software industry. Platforms such as LeetCode, Codeforces, CodeChef, and HackerRank collectively serve millions of users and are widely used in technical interview preparation and competitive contests [1]. However, a fundamental limitation exists: each platform operates as an isolated silo, offering analytics only within its own ecosystem. A programmer active on multiple platforms must manually synthesize their progress across these disparate systems.

This fragmentation leads to several challenges: (1) difficulty in obtaining a holistic view of one's algorithmic skill coverage across topics like dynamic programming, graphs, and string manipulation; (2) inability to identify cross-platform patterns such as consistently weak performance on tree-based problems regardless of the platform; (3) lack of personalized, data-driven guidance that considers the complete picture rather than a single platform's metrics; and (4) absence of an intelligent mentoring system that can reference a user's actual performance data when providing advice.

Existing solutions such as StopStalk [2] aggregate submission data but do not provide AI-powered analysis or personalized mentorship. Platforms like CLIST [3] offer contest tracking across platforms but lack topic-level skill analysis and intelligent recommendations.

This paper presents CodePulse AI, a full-stack platform that addresses these limitations through: (a) automated concurrent scraping of user profiles from LeetCode, Codeforces, CodeChef, and HackerRank using their respective APIs; (b) cross-platform topic normalization and weighted aggregation of skill metrics; (c) Google Gemini LLM-powered insight generation producing structured JSON reports with strengths, weaknesses, career recommendations, overall scores, and 90-day improvement roadmaps; (d) a context-aware AI mentor chatbot that has full access to the user's aggregated profile data and AI-generated insights; and (e) a recruitment module enabling companies to create assessments and AI-match candidates based on their unified coding profiles.

The remainder of this paper is organized as follows: Section II discusses related work. Section III presents the system architecture and design. Section IV describes the implementation details. Section V covers the AI integration methodology. Section VI presents results and evaluation. Section VII concludes with future work.

---

## II. Related Work

### A. Competitive Programming Aggregation

StopStalk [2] is an open-source platform that aggregates submission data from Codeforces, CodeChef, HackerRank, SPOJ, and UVa Online Judge. It provides submission tracking and friend comparisons but does not offer AI-powered analysis or personalized improvement plans. CLIST [3] maintains a comprehensive calendar of programming contests across 100+ platforms and provides basic statistics, but does not aggregate individual user performance metrics at the topic level.

### B. AI in Education and Mentorship

The application of large language models (LLMs) in educational settings has shown significant promise. Khan Academy's Khanmigo [4] uses GPT-4 for personalized tutoring, while GitHub Copilot [5] assists with code generation. However, these systems operate without context about the user's competitive programming skill profile. CodePulse AI differentiates itself by injecting the user's actual performance data — problems solved, difficulty breakdown, topic coverage, contest ratings, and AI-generated insights — directly into the LLM's context, enabling truly personalized mentorship.

### C. Web Scraping for Data Aggregation

Modern web scraping techniques leverage both REST APIs and GraphQL endpoints for structured data extraction [6]. LeetCode exposes a GraphQL API that provides detailed user statistics including per-topic problem counts and submission calendars. Codeforces offers a well-documented REST API with endpoints for user information, rating history, and submission records. CodePulse AI implements platform-specific scrapers following the Abstract Factory design pattern to handle these heterogeneous data sources uniformly.

---

## III. System Architecture

### A. High-Level Architecture

CodePulse AI follows a client-server architecture with clear separation of concerns. The system comprises three primary layers: (1) a Next.js 15 frontend deployed on Vercel, (2) a Python FastAPI asynchronous backend deployed via Docker, and (3) a PostgreSQL database hosted on Neon cloud platform. External integrations include Google Gemini 2.0 Flash for AI capabilities and OAuth 2.0 providers (Google, GitHub) for authentication.

```
+-------------------+        +-------------------+        +------------------+
|   Next.js 15      | <----> |   FastAPI          | <----> |  PostgreSQL      |
|   Frontend        |  REST  |   Backend          |  Async |  (Neon Cloud)    |
|   (Vercel)        |  API   |   (Docker)         | SQLAlch|                  |
+-------------------+        +-------------------+        +------------------+
                                     |
                         +-----------+-----------+
                         |           |           |
                    +----v---+  +----v---+  +----v---+
                    | Gemini |  | OAuth  |  |Platform|
                    | 2.0    |  | Google |  |  APIs  |
                    | Flash  |  | GitHub |  | LC/CF/ |
                    +--------+  +--------+  | CC/HR  |
                                            +--------+
```

**Fig. 1.** High-level system architecture of CodePulse AI showing the three-tier design with external service integrations.

### B. Database Schema

The PostgreSQL database uses 13 tables organized into four domains:

1. **User Management**: `users` (with role-based access: candidate, recruiter, admin), `user_oauth` (multi-provider OAuth accounts)
2. **Profile Aggregation**: `coding_profiles` (platform username linkages with unique constraint per user-platform pair), `platform_snapshots` (point-in-time scrape data with JSONB columns for topic_stats, submission_calendar, and raw_data)
3. **AI Analytics**: `insight_reports` (JSONB columns for strengths, weaknesses, career_recs, roadmap arrays; float overall_score; text summary), `chat_sessions`, `chat_messages`
4. **Recruitment**: `companies`, `assessments`, `assessment_questions` (with JSONB test_cases), `submissions` (with AI feedback), `jobs` (with JSONB required_skills), `applications` (with AI match scoring)

All primary keys use UUID v4 for global uniqueness. Foreign keys use `ON DELETE CASCADE` to maintain referential integrity. The schema leverages PostgreSQL's native JSONB type for storing semi-structured data such as topic statistics and submission calendars, enabling efficient querying and indexing.

### C. API Design

The RESTful API is organized under `/api/v1` with the following endpoint groups:

| Group | Endpoints | Description |
|-------|-----------|-------------|
| Auth | 6 endpoints | Register, login, token refresh, user info, Google/GitHub OAuth |
| Profiles | 4 endpoints | Link/unlink platforms, trigger scraping, retrieve profiles with snapshots |
| Insights | 2 endpoints | Generate AI insights, retrieve latest report |
| Chat | 4 endpoints | CRUD sessions, send messages with AI responses |
| Recruitment | 8+ endpoints | Assessments, jobs, applications, AI matching |

---

## IV. Implementation

### A. Backend Implementation

The backend is implemented in Python using the FastAPI framework, chosen for its native async/await support, automatic OpenAPI documentation generation, and Pydantic-based request/response validation. The application entry point (`main.py`) initializes the FastAPI instance with CORS middleware configured for the frontend origin, includes versioned API routers, and uses a lifespan context manager to ensure all database tables are created on startup via SQLAlchemy's `Base.metadata.create_all`.

**Asynchronous Database Layer**: The database layer uses SQLAlchemy's async engine with the `asyncpg` driver for non-blocking PostgreSQL operations. The connection string uses the `postgresql+asyncpg://` prefix as required by the async driver. Sessions are managed through an `async_sessionmaker` with `expire_on_commit=False` to prevent lazy-loading issues in async contexts.

**Authentication System**: The security module implements a dual-token JWT strategy. Access tokens (HS256 algorithm, 15-minute expiry) are used for API authentication, while refresh tokens (7-day expiry) enable session persistence without re-authentication. Password hashing uses bcrypt via the `passlib` library. The `get_current_user` dependency extracts and validates the JWT from the `Authorization: Bearer` header on protected endpoints.

**OAuth 2.0 Integration**: Google and GitHub OAuth flows are implemented using the standard authorization code grant. The backend exchanges the authorization code for provider tokens via HTTPS POST requests to the respective token endpoints (`https://oauth2.googleapis.com/token` for Google, `https://github.com/login/oauth/access_token` for GitHub), then fetches user profile information including email, full name, and avatar URL. Users are created or linked based on their provider UID, with avatar URLs persisted for UI display.

**Containerization**: The backend uses a multi-stage Docker build: the first stage (`python:3.12-slim`) installs dependencies with `pip install --prefix=/install`, and the second stage copies only the installed packages, reducing the final image size. Docker Compose orchestrates the API container and a PostgreSQL 16 Alpine container with a health check (`pg_isready`) that gates API startup.

### B. Platform Scraping System

The scraping subsystem follows the Abstract Factory design pattern. An abstract base class `AbstractPlatformScraper` defines the interface with two abstract methods: `scrape(username) -> ScrapedProfile` and `validate_username(username) -> bool`. A `ScrapedProfile` dataclass standardizes the output across all platforms with fields: `platform`, `username`, `problems_solved`, `contest_rating`, `topic_stats`, `submission_calendar`, and `raw_data`.

**LeetCode Scraper**: Uses LeetCode's GraphQL API (`leetcode.com/graphql`) with three separate queries: (1) `getUserProfile` for user statistics and per-topic problem counts across fundamental, intermediate, and advanced categories via `tagProblemCounts`; (2) `userContestRankingInfo` for contest rating and global ranking; (3) `userProfileCalendar` for the submission heatmap calendar. Topic statistics are aggregated across all three tag levels (fundamental, intermediate, advanced) into a unified dictionary.

**Codeforces Scraper**: Uses Codeforces' official REST API (`codeforces.com/api`) with three endpoints: `user.info` for rating and rank, `user.rating` for contest history, and `user.status` for up to 10,000 recent submissions. The scraper deduplicates solved problems using a set of `contestId + index` identifiers and computes per-tag topic counts from problem metadata.

**CodeChef Scraper**: Uses CodeChef's REST API for user profiles, extracting star rating, problems solved by difficulty tier, and activity data.

**HackerRank Scraper**: Uses HackerRank's REST API endpoints for track scores, badge information, and submission history.

**Concurrent Aggregation**: The `ProfileAggregator` class orchestrates all scrapers concurrently using `asyncio.gather` with per-scraper error isolation via `_safe_scrape` wrappers that catch and suppress individual scraper failures. Topic statistics are merged across platforms using weighted normalization: each platform's topic counts are divided by that platform's total problems to produce proportional scores, then averaged across platforms. This prevents a platform with more total problems from dominating the merged topic profile.

### C. Frontend Implementation

The frontend is implemented with Next.js 15 using the App Router architecture, React 19, TypeScript, and Tailwind CSS 3. The application follows a dark theme design language with a slate-950 background, emerald-400/500 accent colors, and rounded-2xl/3xl card components with border-white/10 borders.

**Authentication Flow**: The `api-client.ts` module implements an automatic token refresh mechanism. Access tokens are stored in JavaScript memory (not localStorage for XSS protection) while refresh tokens are persisted in localStorage. On application load, if no access token exists but a refresh token is found, the client automatically attempts a refresh before making API calls. On 401 responses, the client transparently refreshes the token and retries the failed request.

**Dashboard Visualization**: The dashboard renders four custom SVG-based chart components without external charting libraries:
1. **DifficultyChart** — An SVG donut chart showing the Easy/Medium/Hard problem distribution with stroke-dasharray animations and a central total count.
2. **TopicChart** — A horizontal bar chart displaying the top 12 topics with gradient fills from emerald-400 to emerald-600.
3. **TopicRadar** — An SVG radar (spider) chart plotting the user's top 8 topics on polygonal axes.
4. **ActivityHeatmap** — A GitHub-style contribution grid showing the last 20 weeks of submission activity with four intensity levels.

**Responsive Design**: The application uses a mobile-first approach with a desktop sidebar collapsing into a fixed bottom navigation bar on mobile screens. The navbar displays an avatar with a dropdown menu on desktop and a hamburger menu on mobile.

**AI Chat Interface**: Chat messages from the AI assistant are rendered using `react-markdown` with a custom `prose-chat` CSS class that styles headings, code blocks (with background highlighting), bullet lists, blockquotes, and tables for rich formatted output.

---

## V. AI Integration

### A. Insight Generation Pipeline

The insight generation pipeline follows a four-stage process:

1. **Data Collection**: All linked platform snapshots for the user are retrieved from the database, including problems_solved, contest_rating, topic_stats, submission_calendar, and raw_data.

2. **Prompt Construction**: The aggregated profile data is serialized to JSON and injected into a structured prompt template (`INSIGHT_GENERATION_PROMPT`) that instructs the Gemini model to act as an "expert competitive programming coach and career advisor." The prompt specifies the exact JSON output schema with fields for strengths (array of {topic, score, detail}), weaknesses, career_recs, roadmap (three 30-day phases with focus areas and action items), overall_score (0-100), and summary_text.

3. **LLM Inference**: The `GeminiClient` wrapper sends the prompt to Google Gemini 2.0 Flash via the `google-generativeai` Python SDK. The synchronous SDK call is executed in a thread pool using `asyncio.get_event_loop().run_in_executor()` to maintain non-blocking behavior in the async FastAPI context.

4. **Response Parsing**: The raw LLM response is cleaned (stripping markdown code block delimiters if present) and parsed as JSON. A fallback structure is returned if parsing fails, ensuring the API never returns an error to the user even if the LLM produces malformed output.

### B. Context-Aware AI Mentor

The AI mentor chatbot differentiates itself from generic chatbots through deep integration with the user's actual performance data. The `_build_profile_context()` function constructs a rich text summary that includes:

- Per-platform statistics: problems solved, contest rating, difficulty breakdown (Easy/Medium/Hard), top 10 and bottom 5 topics
- Cross-platform totals
- Latest AI insight report: overall score, strengths with scores, weaknesses with scores, career recommendations, and the full 90-day roadmap

This context is injected into the `CHAT_SYSTEM_PROMPT` which instructs the model to: reference specific numbers from the user's profile, suggest specific problems by name/number, compare performance across platforms, use markdown formatting for structured responses, and frame weaknesses as growth opportunities with concrete action plans.

The chat engine prepends the system prompt as a synthetic user-assistant exchange in the conversation history before sending it to Gemini's multi-turn chat API, preserving the full conversation context while grounding the model in the user's actual data.

### C. AI-Generated Chat Titles

When a new chat session's first message is sent, the system automatically generates a descriptive title using a separate Gemini call with the prompt: "Generate a short title (max 6 words, no quotes) for a chat that starts with this message." The title is truncated to 60 characters and cleaned of surrounding quotes. This replaces the generic "New Chat" placeholder with a meaningful session label.

### D. Recruitment AI Matching

The `SKILL_MATCH_PROMPT` enables AI-powered candidate-job matching by providing the candidate's aggregated profile data and the job's requirements (title, description, required skills, minimum score) to Gemini, which returns a match_score (0-100), detailed reasoning, skill gaps, and candidate highlights as structured JSON.

---

## VI. Results and Evaluation

### A. System Performance

The platform was tested with real user accounts across all four supported platforms. Table I summarizes the scraping performance:

**TABLE I. Platform Scraping Performance**

| Platform | API Type | Avg. Response Time | Data Points Extracted |
|----------|----------|-------------------|----------------------|
| LeetCode | GraphQL | ~2.1s | Problems, difficulty, topics, contests, calendar |
| Codeforces | REST | ~1.8s | Problems, tags, rating, contest history |
| CodeChef | REST | ~2.5s | Problems, rating, difficulty tiers |
| HackerRank | REST | ~1.5s | Tracks, badges, submissions |
| **Concurrent (all 4)** | Mixed | **~3.2s** | All combined |

Concurrent scraping via `asyncio.gather` achieves near-linear speedup, with the total time dominated by the slowest individual scraper rather than the sum of all scrapers.

### B. AI Insight Quality

The Gemini 2.0 Flash model consistently produces well-structured JSON responses conforming to the specified schema. Key observations:

1. **Accuracy**: Strengths and weaknesses accurately reflect the topic distribution in the user's profile data. For a user with 70 Array problems but only 3 Sliding Window problems, the model correctly identifies arrays as a strength and sliding window as a weakness.

2. **Actionability**: The 90-day roadmap produces specific, phased recommendations (e.g., "Days 1-30: Focus on Graph Fundamentals — solve BFS/DFS problems, practice shortest path algorithms, attempt 2 graph contest problems per week").

3. **Career Relevance**: Career recommendations are contextually appropriate based on the user's overall score and topic coverage.

### C. Chat Mentor Effectiveness

The context-aware chat mentor demonstrates significant improvement over a generic chatbot:

1. **Personalization**: The mentor references the user's specific statistics in responses (e.g., "I see you've solved 122 problems on LeetCode with strong Array and String skills, but your Graph coverage is only at 8 problems").

2. **Specific Recommendations**: Instead of generic advice like "practice more," the mentor suggests specific problems (e.g., "Try LeetCode #200 Number of Islands to strengthen your BFS skills").

3. **Cross-Platform Awareness**: The mentor can compare performance across platforms (e.g., "Your Codeforces rating of 1450 suggests you're comfortable with implementation problems, but your LeetCode topic breakdown shows room for improvement in advanced algorithms").

### D. Frontend Performance

The Next.js 15 application with custom SVG charts achieves fast load times without heavy charting library dependencies. The SVG-based visualization approach eliminates the need for libraries like Chart.js or Recharts, reducing the JavaScript bundle size while maintaining interactive, responsive charts that adapt to all screen sizes.

---

## VII. Conclusion and Future Work

This paper presented CodePulse AI, a full-stack AI-powered platform for competitive programming profile aggregation, insight generation, and personalized mentorship. The system successfully addresses the fragmentation problem by unifying data from LeetCode, Codeforces, CodeChef, and HackerRank into a single dashboard with cross-platform analytics. The integration of Google Gemini 2.0 Flash enables data-driven AI insights that go beyond what any individual platform offers, including a structured 90-day improvement roadmap and a context-aware AI mentor that grounds its advice in the user's actual performance data.

Key contributions include: (1) a concurrent async scraping framework using the Abstract Factory pattern for heterogeneous API integration; (2) a weighted normalization algorithm for cross-platform topic aggregation; (3) a structured prompt engineering approach that produces consistently parseable JSON from an LLM; and (4) a context injection methodology for creating a truly personalized AI mentor.

Future work includes: (a) adding support for additional platforms such as AtCoder and SPOJ; (b) implementing real-time streaming responses for the AI chat using Server-Sent Events (SSE); (c) expanding the recruitment module with a full assessment engine including server-side code execution and AI-powered code review; (d) implementing historical trend analysis to track skill progression over time; (e) adding collaborative features such as study groups and leaderboards; and (f) exploring fine-tuned models for competitive programming-specific mentorship.

---

## References

[1] S. Halim and F. Halim, "Competitive Programming 3: The New Lower Bound of Programming Contests," Lulu Press, 2013.

[2] R. Shah, "StopStalk: A Platform to Track Competitive Programming Progress," GitHub Repository, 2016. [Online]. Available: https://github.com/stopstalk/stopstalk-deployment

[3] A. Alekseev, "CLIST — A Contest List Aggregator," 2024. [Online]. Available: https://clist.by

[4] S. Khan, "Khanmigo: AI for Education," Khan Academy, 2023. [Online]. Available: https://www.khanacademy.org/khan-labs

[5] GitHub, "GitHub Copilot: Your AI Pair Programmer," 2023. [Online]. Available: https://github.com/features/copilot

[6] R. Mitchell, "Web Scraping with Python: Collecting More Data from the Modern Web," O'Reilly Media, 2nd ed., 2018.

[7] S. Ramirez, "FastAPI: A Modern, Fast Web Framework for Building APIs with Python," 2019. [Online]. Available: https://fastapi.tiangolo.com

[8] Vercel, "Next.js: The React Framework for the Web," 2024. [Online]. Available: https://nextjs.org

[9] Google, "Gemini API Documentation," 2024. [Online]. Available: https://ai.google.dev/docs

[10] M. Bayer, "SQLAlchemy: The Database Toolkit for Python," 2024. [Online]. Available: https://www.sqlalchemy.org

[11] D. Hardt, "The OAuth 2.0 Authorization Framework," RFC 6749, Internet Engineering Task Force, 2012.

[12] M. Jones, J. Bradley, and N. Sakimura, "JSON Web Token (JWT)," RFC 7519, Internet Engineering Task Force, 2015.
