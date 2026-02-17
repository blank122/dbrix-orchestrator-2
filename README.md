# 🚀 Deployment Architecture

This project uses a simple and production-ready cloud stack:

- **Frontend:** Vercel  
- **Backend Proxy:** Render  
- **AI Agent Hosting:** Databricks Model Serving  

---

## 🏗 Architecture Overview

User
↓
Vercel (React Frontend)
↓
Render (FastAPI Backend Proxy)
↓
Databricks Model Serving Endpoint
↓
Databricks AI Agent (Genie / Custom RAG)


---

## 🔄 Request Flow

1. User interacts with the frontend hosted on Vercel.
2. The frontend sends a `POST` request to the backend hosted on Render.
3. The backend:
   - Validates request origin (CORS)
   - Attaches `DATABRICKS_TOKEN`
   - Transforms payload to Databricks format
4. The request is forwarded to the Databricks Serving endpoint.
5. The Databricks Agent processes the query.
6. The backend streams the response back to the frontend.

---

# 🌍 Deployment Details

## Frontend – Vercel

- Hosts the React application
- Communicates only with the backend (never directly with Databricks)

Example environment variable:


---

## Backend – Render

Render hosts the FastAPI proxy service.

### Build Command


### Required Environment Variables (Set in Render Dashboard)

DATABRICKS_HOST
DATABRICKS_TOKEN
AGENT_ENDPOINT_URL
ALLOWED_ORIGINS=https://agentic-fis.vercel.app


⚠️ Never commit `.env` to GitHub.

---

## AI Agent Hosting – Databricks

- Agents are deployed via Databricks Model Serving.
- The backend forwards requests to:


- Authentication is handled using a Personal Access Token (PAT).
- The token is securely stored in Render environment variables.

---

# 🔐 Security Model

| Layer | Responsibility |
|-------|---------------|
| Vercel | UI only — no secrets stored |
| Render | Stores and protects Databricks credentials |
| Databricks | Executes AI agent logic |

Security guarantees:

- Frontend never sees `DATABRICKS_TOKEN`
- CORS restricts allowed origins
- Tokens stored securely in Render
- All communication is HTTPS

---

# 📈 Why This Stack Works

**Vercel**
- Global CDN
- Seamless GitHub CI/CD
- Ideal for React frontends

**Render**
- Simple Python backend deployment
- Automatic HTTPS
- Easy environment variable management

**Databricks**
- Scalable AI model serving
- Enterprise-grade security
- Supports custom AI agents (Genie / RAG pipelines)

---

# 🔄 Optional Production Improvements

- Add rate limiting middleware
- Enable structured logging
- Add health check endpoint (`/health`)
- Configure auto-scaling on Render
- Rotate Databricks tokens periodically
