# Oura API Integration - Testing Guide

This guide helps you test the Oura OAuth2 authentication and features available in this project.

## 1. Prerequisites / Setup

Before testing, ensure your `.env` file is configured:

```env
OURA_CLIENT_ID=your_client_id_from_oura_cloud
OURA_CLIENT_SECRET=your_client_secret_from_oura_cloud
OURA_REDIRECT_URI=http://localhost:8000/auth/callback
```

Make sure you have added `http://localhost:8000/auth/callback` to your Redirect URIs in the [Oura Cloud Developer Console](https://cloud.ouraring.com/oauth/applications).

## 1.1. No Ring? Use Sandbox Mode!

If you do not have an Oura Ring but want to see data:

1.  **Create an Oura Account**: Download the Oura App on your phone and sign up (you can skip ring pairing).
2.  **Enable Sandbox**: Add this to your `.env` file:
    ```env
    OURA_SANDBOX_MODE=True
    ```
    This will redirect all API calls to the Oura Sandbox, which returns sample data even for accounts without a ring.

## 2. Starting the Server

Run the start script:

```bash
./run.sh
```

Or manually:

```bash
conda run -n oura-env uvicorn main:app --reload --port 8000
```

## 3. Testing OAuth2 Authentication

1.  Open your browser and navigate to: `http://localhost:8000/auth/login`
2.  You will be redirected to the Oura Login page.
3.  Log in with your Oura account credentials.
4.  Authorize the application.
5.  You will be redirected back to `http://localhost:8000/auth/callback`.
6.  The browser will display a JSON response containing your **Access Token**.
    - **Action**: Copy this `access_token` string. You will need it to test features.

## 4. Testing Features (via Swagger UI)

We use Swagger UI to interact with the API endpoints easily.

1.  Navigate to: `http://localhost:8000/docs`
2.  You will be redirected to the API docs.
3.  You will see a list of available endpoints.

### Available Features / Endpoints

| Feature            | Endpoint         | Description                                       |
| :----------------- | :--------------- | :------------------------------------------------ |
| **Personal Info**  | `/api/user`      | Basic user details (age, weight, height, email).  |
| **Sleep Data**     | `/api/sleep`     | Deep sleep, REM, light sleep, timing, efficiency. |
| **Daily Activity** | `/api/activity`  | Steps, calories, varying intensity activities.    |
| **Readiness**      | `/api/readiness` | Recovery index, sleep balance, activity balance.  |
| **Webhooks**       | `/webhook`       | Receives real-time updates (requires ngrok).      |

### How to Test an Endpoint

1.  Click on an endpoint (e.g., `GET /api/sleep`).
2.  Click **Try it out**.
3.  Paste your access token into the `token` field (or header).
4.  (Optional) Adjust `start_date` and `end_date`.
5.  Click **Execute**.
6.  Scroll down to **Response body** to see the real data from Oura.

## 5. Webhooks (Optional)

To test webhooks:

1.  Install `ngrok`.
2.  Run `ngrok http 8000`.
3.  Copy the HTTPS URL (e.g., `https://abcdef.ngrok.io`).
4.  Go to Oura Cloud Console and register a webhook with URL: `https://abcdef.ngrok.io/webhook`.
5.  When new data syncs from your ring, logs will appear in the server terminal.

## 6. Oura API Capabilities Reference

The Oura API provides the following data types (some implemented here, others available to add):

- **Daily Sleep**: Detailed sleep stages and scores.
- **Daily Activity**: Activity levels, metabolic equivalent, inactive times.
- **Daily Readiness**: Indicators of how ready you are for the day.
- **Heart Rate**: 24/7 heart rate trends (requires Personal Access Token or approved App).
- **SpO2**: Blood oxygen levels during sleep.
- **Stress**: Daily stress levels.
- **Workouts**: Automatically or manually detected workouts.
