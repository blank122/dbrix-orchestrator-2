import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# VERY IMPORTANT: Allow your React app to talk to this backend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5174",  # Your React/Vite port from the error
#         "http://127.0.0.1:5174",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

origins = [
    "http://localhost:5173",  # The origin for your React app on your local machine/development environment
    "https://agentic-fis.vercel.app",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # <-- use "*" for debugging first
    allow_headers=["*"],  # <-- use "*" for debugging first
    max_age=3600,  # Cache preflight response for 1 hour (3600 seconds)
)

@app.get("/test-connection")
async def test_databricks():
    token = os.getenv("DATABRICKS_TOKEN")
    url = os.getenv("DATABRICKS_ENDPOINT_URL")

    # UPDATED: match the working Databricks schema
    payload = {
        "input": [
            {
                "role": "user",
                "content": "Compare Equity vs Loan investment across industries."
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return {
            "status": "Connected to Databricks Successfully",
            "databricks_response": response.json()
        }
    except Exception as e:
        return {"status": "Failed", "error": str(e)}

@app.post("/ask")
async def ask_orchestrator(data: dict):
    token = os.getenv("DATABRICKS_TOKEN")
    url = os.getenv("DATABRICKS_ENDPOINT_URL")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # NEW: normalize frontend payload into Databricks agent format
    user_input = data.get("input") or data.get("message") or data.get("text")
    if user_input is None:
        raise HTTPException(status_code=400, detail="Missing 'input' field in request body")

    if isinstance(user_input, list):
        # If the frontend already sends the full list-of-messages, just pass it through
        payload = {"input": user_input}
    else:
        # Wrap a single user string into the required list-of-messages structure
        payload = {
            "input": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

    # Modified for better stability
    try:
        # Use a session for better performance/connection pooling
        with requests.Session() as session:
            response = session.post(url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            return response.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Databricks agent took too long to respond.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
