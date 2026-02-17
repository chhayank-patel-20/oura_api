import os
import requests
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("OURA_CLIENT_ID")
CLIENT_SECRET = os.getenv("OURA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OURA_REDIRECT_URI", "http://localhost:8000/auth/callback")
SANDBOX_MODE = os.getenv("OURA_SANDBOX_MODE", "False").lower() == "true"

BASE_URL = "https://api.ouraring.com/v2/sandbox" if SANDBOX_MODE else "https://api.ouraring.com/v2"

app = FastAPI(title="Oura API Test", description="FastAPI backend to test Oura Ring API integration")

# Add CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for simple token management (NOT for production)
# In a real app, use a database or secure session storage.
access_token_storage = {"token": None}

@app.get("/")
def home():
    return {
        "message": "Welcome to Oura API Test", 
        "steps": [
            "1. Go to /auth/login to authenticate",
            "2. Copy the access token",
            "3. Use Swagger UI at /docs to test endpoints with the token"
        ]
    }

@app.get("/privacy")
def privacy():
    """Privacy Policy placeholder."""
    return {"message": "This is a test application. No real user data is shared or sold."}

@app.get("/terms")
def terms():
    """Terms of Service placeholder."""
    return {"message": "This is a test application for personal use only."}

# --- Authentication ---

@app.get("/auth/login")
def login():
    """Redirects user to Oura OAuth2 authorization page."""
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="OURA_CLIENT_ID not set in .env")
    
    # Scopes from Oura Developer Portal example
    auth_url = (
        f"https://cloud.ouraring.com/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state=random_state_string"
        f"&scope=email+personal+daily+heartrate+tag+workout+session+spo2+ring_configuration+stress+heart_health"
    )
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
def callback(code: str, state: str = None):
    """Exchanges authorization code for access token."""
    url = "https://api.ouraring.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    
    response = requests.post(url, data=data)
    if response.status_code != 200:
        return JSONResponse(status_code=400, content={"error": "Failed to retrieve token", "details": response.json()})
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    
    # Store globally for simplicity in this test session
    access_token_storage["token"] = access_token
    
    return {
        "message": "Authentication successful!",
        "access_token": access_token, 
        "instructions": "Copy this token and authorize in Swagger UI or pass it to API endpoints.",
        "full_response": token_data
    }

# --- API Wrappers ---

def get_headers(token: str = None):
    # Prefer passed token, fallback to stored token
    actual_token = token or access_token_storage["token"]
    if not actual_token:
        raise HTTPException(status_code=401, detail="Missing access token. Please login first.")
    return {"Authorization": f"Bearer {actual_token}"}

@app.get("/api/user")
def get_user_info(token: str = None):
    """Fetch logged in user information."""
    headers = get_headers(token)
    response = requests.get(f"{BASE_URL}/usercollection/personal_info", headers=headers)
    return response.json()

@app.get("/api/sleep")
def get_sleep_data(start_date: str = "2023-01-01", end_date: str = "2024-01-01", token: str = None):
    """Fetch sleep data for a date range."""
    headers = get_headers(token)
    params = {"start_date": start_date, "end_date": end_date}
    response = requests.get(f"{BASE_URL}/usercollection/sleep", headers=headers, params=params)
    return response.json()

@app.get("/api/activity")
def get_activity_data(start_date: str = "2023-01-01", end_date: str = "2024-01-01", token: str = None):
    """Fetch daily activity data."""
    headers = get_headers(token)
    params = {"start_date": start_date, "end_date": end_date}
    response = requests.get(f"{BASE_URL}/usercollection/daily_activity", headers=headers, params=params)
    return response.json()

@app.get("/api/readiness")
def get_readiness_data(start_date: str = "2023-01-01", end_date: str = "2024-01-01", token: str = None):
    """Fetch daily readiness data."""
    headers = get_headers(token)
    params = {"start_date": start_date, "end_date": end_date}
    response = requests.get(f"{BASE_URL}/usercollection/daily_readiness", headers=headers, params=params)
    return response.json()


# --- Webhooks ---

# In-memory storage for recent webhooks (Ephemeral on serverless)
recent_webhooks = []

from datetime import datetime

@app.post("/webhook")
async def webhook_listener(request: Request):
    """Endpoint to receive webhook events from Oura."""
    try:
        payload = await request.json()
        logger.info(f"Webhook received: {payload}")
        
        # Store for viewing in UI
        recent_webhooks.append({
            "received_at": datetime.now().isoformat(),
            "payload": payload
        })
        # Keep only last 10
        if len(recent_webhooks) > 10:
            recent_webhooks.pop(0)
        
        return {"status": "received", "payload": payload}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")

@app.get("/webhooks/recent")
def get_recent_webhooks():
    """View the last 10 webhooks received by this instance."""
    return recent_webhooks

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
