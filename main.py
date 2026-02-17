import os
import requests
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("OURA_CLIENT_ID")
CLIENT_SECRET = os.getenv("OURA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OURA_REDIRECT_URI", "http://localhost:8000/auth/callback")
SANDBOX_MODE = os.getenv("OURA_SANDBOX_MODE", "False").lower() == "true"

BASE_URL = "https://api.ouraring.com/v2/sandbox" if SANDBOX_MODE else "https://api.ouraring.com/v2"

# Security Scheme for Swagger UI
security = HTTPBearer()

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

# In-memory storage for simple token management
access_token_storage = {"token": None}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Oura API Test</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
                .btn { display: inline-block; padding: 10px 20px; background-color: #0070f3; color: white; text-decoration: none; border-radius: 5px; }
                .btn:hover { background-color: #0051a2; }
                code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>💍 Oura API Test</h1>
            <p>Welcome! This application allows you to test the Oura Ring API.</p>
            
            <h2>1. Authentication</h2>
            <p><a href="/auth/login" class="btn">Login with Oura</a></p>
            
            <h2>2. Documentation</h2>
            <p>You can find the API documentation and Swagger UI here: <a href="/docs">/docs</a></p>
            
            <h2>3. Simple Dashboard</h2>
            <p>Once logged in, you will be redirected to the <a href="/ui">/ui</a> dashboard.</p>
        </body>
    </html>
    """

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
    
    print(f"Authentication Successful! Token Data: {token_data}")
    
    # Store globally for simplicity
    access_token_storage["token"] = access_token
    
    # Redirect to UI with token in hash (so client JS can pick it up)
    return RedirectResponse(url=f"/ui#access_token={access_token}")

# --- UI Endpoint ---

@app.get("/ui", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Oura Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f9fafb; }
            h1 { color: #111; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .btn { cursor: pointer; padding: 8px 16px; background-color: #0070f3; color: white; border: none; border-radius: 4px; font-size: 14px; }
            .btn:hover { background-color: #0051a2; }
            pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; max-height: 300px; font-size: 13px; }
            .flex { display: flex; gap: 10px; flex-wrap: wrap; }
            .hidden { display: none; }
            #token-display { font-family: monospace; word-break: break-all; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <h1>💍 Oura Dashboard</h1>
        
        <div class="card" id="auth-section">
            <h2>Authentication</h2>
            <div id="logged-out">
                <p>You are not logged in.</p>
                <a href="/auth/login" class="btn">Login with Oura</a>
            </div>
            <div id="logged-in" class="hidden">
                <p>✅ <strong>Logged In</strong></p>
                <p>Access Token: <span id="token-display"></span></p>
            </div>
        </div>

        <div class="card">
            <h2>Actions</h2>
            <div class="flex">
                <button class="btn" onclick="fetchData('/api/user')">Fetch User Info</button>
                <button class="btn" onclick="fetchData('/api/sleep')">Fetch Sleep</button>
                <button class="btn" onclick="fetchData('/api/activity')">Fetch Activity</button>
                <button class="btn" onclick="fetchData('/api/readiness')">Fetch Readiness</button>
            </div>
            <h3>Result:</h3>
            <pre id="api-result">Click a button above to see data...</pre>
        </div>

        <div class="card">
            <h2>Recent Webhooks</h2>
            <button class="btn" onclick="fetchWebhooks()">Refresh Webhooks</button>
            <pre id="webhook-result">Loading...</pre>
        </div>

        <script>
            let accessToken = null;

            // 1. Check for token in URL hash (from callback redirect)
            const hash = window.location.hash;
            if (hash.includes("access_token=")) {
                accessToken = hash.split("access_token=")[1].split("&")[0];
                window.localStorage.setItem("oura_token", accessToken);
                // Clean URL
                window.history.replaceState(null, null, ' ');
            } else {
                // 2. Check local storage
                accessToken = window.localStorage.getItem("oura_token");
            }

            // UI State
            if (accessToken) {
                document.getElementById('logged-out').classList.add('hidden');
                document.getElementById('logged-in').classList.remove('hidden');
                document.getElementById('token-display').innerText = accessToken;
            }

            async function fetchData(endpoint) {
                if (!accessToken) {
                    alert("Please login first!");
                    return;
                }
                
                document.getElementById('api-result').innerText = "Loading...";
                
                try {
                    const res = await fetch(endpoint, {
                        headers: {
                            'Authorization': 'Bearer ' + accessToken
                        }
                    });
                    const data = await res.json();
                    document.getElementById('api-result').innerText = JSON.stringify(data, null, 2);
                } catch (err) {
                    document.getElementById('api-result').innerText = "Error: " + err.message;
                }
            }
            
            async function fetchWebhooks() {
                try {
                    const res = await fetch('/webhooks/recent');
                    const data = await res.json();
                    document.getElementById('webhook-result').innerText = JSON.stringify(data, null, 2);
                } catch (err) {
                    document.getElementById('webhook-result').innerText = "Error loading webhooks.";
                }
            }
            
            // Allow polling webhooks
            setInterval(fetchWebhooks, 5000);
            fetchWebhooks();

        </script>
    </body>
    </html>
    """

# --- API Wrappers ---

def get_headers(token: str = None, auth: HTTPAuthorizationCredentials = None):
    # Resolving token priority:
    # 1. Direct argument 'token' (legacy/manual)
    # 2. Authorization Header 'auth' (Swagger/UI)
    # 3. Stored global token
    
    actual_token = token
    if not actual_token and auth:
        actual_token = auth.credentials
    if not actual_token:
        actual_token = access_token_storage["token"]
        
    if not actual_token:
        raise HTTPException(status_code=401, detail="Missing access token. Please login first.")
    return {"Authorization": f"Bearer {actual_token}"}

@app.get("/api/user")
def get_user_info(token: str = None, auth: HTTPAuthorizationCredentials = Depends(security)):
    """Fetch logged in user information."""
    headers = get_headers(token, auth)
    response = requests.get(f"{BASE_URL}/usercollection/personal_info", headers=headers)
    return response.json()

@app.get("/api/sleep")
def get_sleep_data(start_date: str = "2023-01-01", end_date: str = "2024-01-01", token: str = None, auth: HTTPAuthorizationCredentials = Depends(security)):
    """Fetch sleep data for a date range."""
    headers = get_headers(token, auth)
    params = {"start_date": start_date, "end_date": end_date}
    response = requests.get(f"{BASE_URL}/usercollection/sleep", headers=headers, params=params)
    return response.json()

@app.get("/api/activity")
def get_activity_data(start_date: str = "2023-01-01", end_date: str = "2024-01-01", token: str = None, auth: HTTPAuthorizationCredentials = Depends(security)):
    """Fetch daily activity data."""
    headers = get_headers(token, auth)
    params = {"start_date": start_date, "end_date": end_date}
    response = requests.get(f"{BASE_URL}/usercollection/daily_activity", headers=headers, params=params)
    return response.json()

@app.get("/api/readiness")
def get_readiness_data(start_date: str = "2023-01-01", end_date: str = "2024-01-01", token: str = None, auth: HTTPAuthorizationCredentials = Depends(security)):
    """Fetch daily readiness data."""
    headers = get_headers(token, auth)
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
