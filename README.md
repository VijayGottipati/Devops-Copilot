# Multi-Agent DevOps Copilot

A comprehensive, event-driven DevOps automation platform orchestrated by a Swarm of AI Agents using LangGraph and powered by Google Gemini 1.5. This system integrates directly with enterprise communication platforms, orchestrates complex CI/CD workflows, manages cloud infrastructure, and requires explicit human-in-the-loop approval strings for critical operations.

## Architecture Overview

The system architecture is decoupled into a robust back-end event processor and an operational command center dashboard.

*   **Backend Engine (Django & LangGraph)**: A Python-based API that serves as the webhook ingestion point for platforms such as GitHub, Slack, Discord, and Gmail. Events are validated, enriched, and pushed onto an AWS SQS message queue for asynchronous processing.
*   **The AI Swarm**: Background workers dequeue payloads and route them to a specialized hierarchy of LangGraph agents (Warden, Architect, Data Engineer, Site Reliability Engineer) parameterized by Gemini 1.5. Agents negotiate execution plans, analyze codebase state via the GitHub API, and generate architectural pull requests.
*   **Frontend Dashboard (Angular)**: A real-time command center providing project context switching, OAuth 2.0 integration management, live swarm execution logs, and an approval queue for pending AI pull requests or infrastructure remediations. 
*   **Data Persistence (PostgreSQL / pgvector)**: State, human-in-the-loop approval thresholds, operational metrics, and encrypted OAuth tokens are securely persisted in a Neon PostgreSQL relational database.

## Key Features

1.  **Multi-Platform Ingestion**: Connects seamlessly with Slack channels, Discord webhooks, or direct GitHub triggers.
2.  **Autonomous Code Generation**: The agentic swarm checks out branches, reads current implementations, writes targeted code, and opens Pull Requests for review automatically.
3.  **Human-in-the-Loop Safeguards**: Critical path operations (deployments, secure schema changes) halt agent execution and await manual approval from designated environment owners via the Angular dashboard or Slack actions.
4.  **Meeting Video Ingestion**: Converts recorded architectural syncs into contextual memory strings using Gemini's multi-modal capabilities.
5.  **GitOps Driven**: All configuration and state changes are handled as code.

## Technology Stack

*   **API Layer**: Django REST Framework
*   **Agentic Framework**: LangGraph, LangChain
*   **Large Language Model**: Google Gemini 1.5 Flash
*   **Queue Mechanics**: AWS Simple Queue Service (SQS)
*   **Database**: Neon Serverless Postgres
*   **Command Center UI**: Angular 18, TailwindCSS
*   **Deployment**: Vercel (Frontend), Render.com (Backend)

## Deployment Instructions

### Prerequisites
*   Node.js (v18+)
*   Python 3.11+
*   PostgreSQL instance

### Backend Setup (Django)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Define environment variables in a `.env` file mapping to your database and provider OAuth keys.
5. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Frontend Setup (Angular)

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Boot the development server:
   ```bash
   npm run start
   ```

## OAuth Integrations

OAuth 2.0 Client Identifiers and Secrets must be provided in the server environment to utilize Gmail and GitHub integration. Configure your respective developer consoles to allow callback URIs pointing to `/api/auth/{provider}/callback/`.

## Author

Developed by Vijay Gottipati.
