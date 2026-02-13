import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import json # Add this at the top

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
    "https://your-production-frontend.com",
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

    try:
        # DEBUG: See what we are sending
        print(f"DEBUG: Sending Payload to Databricks: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=180)
        # DEBUG: See the raw status and content
        print(f"DEBUG: Databricks Status Code: {response.status_code}")
        response.raise_for_status()
        
        result = response.json()
            
        # DEBUG: This is the most important part for your Chart Switcher
        print(f"DEBUG: Raw Databricks Response JSON: {json.dumps(result, indent=2)}")
            
        return result
    
    except requests.exceptions.HTTPError as http_err:
        print(f"DEBUG: HTTP Error occurred: {http_err}")
        print(f"DEBUG: Error Response Body: {response.text}") # See the error message from Databricks
        raise HTTPException(status_code=response.status_code, detail=str(http_err))
    except requests.exceptions.Timeout:
        print("DEBUG: Request timed out after 300 seconds.")
        raise HTTPException(status_code=504, detail="Databricks agent took too long to respond.")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
