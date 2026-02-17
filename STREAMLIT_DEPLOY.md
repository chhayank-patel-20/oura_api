# Deploying the Streamlit UI

You asked a very important question: **Vercel cannot run Streamlit easily.**

- **Vercel** is for "Serverless" functions (perfect for our FastAPI backend).
- **Streamlit** requires a persistent running server (websockets), which Vercel kills after a few seconds.

## The Solution: Split Deployment

We will deploy them separately (which is better architecture anyway):

1.  **Backend (FastAPI)** -> Deployed on **Vercel** (you already have the setup for this).
2.  **Frontend (Streamlit)** -> Deployed on **Streamlit Community Cloud** (Free & One-click).

## Steps to Deploy Streamlit

### 1. Push Code to GitHub

You need your code in a GitHub repository.

### 2. Sign up for Streamlit Cloud

Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.

### 3. Deploy

1.  Click **"New app"**.
2.  Select your Repository, Branch, and Main File path (`streamlit_app.py`).
3.  Click **"Deploy!"**.

### 4. Connect to your Backend

Once your Streamlit app is running:

1.  Open the App.
2.  In the Sidebar "Configuration", change `API Base URL` to your **Vercel Backend URL** (e.g., `https://oura-api-test.vercel.app`).
    - _Note: You can code this default into `streamlit_app.py` or set it as an Environment Variable `API_BASE_URL` in Streamlit Cloud settings._

## Alternative: Docker (Run everything together)

If you _really_ want them on one server, you must use a container service like **Render** or **Railway** with Docker.

1.  Create a `Dockerfile` that installs everything and runs `run.sh`.
2.  Deploy that Docker image.
3.  However, free tiers often limit you to **one open port**, so accessing both port 8000 and 8501 might be tricky without a reverse proxy (Nginx).

**Recommendation**: Stick to **Vercel (Backend)** + **Streamlit Cloud (Frontend)**. It's the standard, easiest free stack.
