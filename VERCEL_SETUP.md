# Deploying to Vercel

Vercel is the easiest way to deploy this FastAPI application. It natively supports Python serverless functions.

## Prerequisites

1.  **Node.js & npm** installed.
2.  **Vercel Account** (Free tier is sufficient).

## Deployment Steps

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

Authenticate the CLI with your account.

```bash
vercel login
```

### 3. Deploy

Run the deploy command from the project root:

```bash
vercel
```

- **Set up and deploy?** [Y/n]: `y`
- **Which scope do you want to deploy to?** Select your account.
- **Link to existing project?** [y/N]: `n`
- **What’s your project’s name?** `oura-api-test` (or similar).
- **In which directory is your code located?** `./` (default).
- **Want to modify these settings?** [y/N]: `n` (Auto-detection usually works, but `vercel.json` forces Python handling).

### 4. Configure Environment Variables

**Crucial Step**: Your app needs the Oura credentials to work.

1.  Go to your Vercel Project Dashboard (link provided in terminal after deploy).
2.  Navigate to **Settings** > **Environment Variables**.
3.  Add the following:
    - `OURA_CLIENT_ID`: Your Oura Client ID.
    - `OURA_CLIENT_SECRET`: Your Oura Client Secret.
    - `OURA_REDIRECT_URI`: The URL provided by Vercel + `/auth/callback` (e.g., `https://oura-api-test.vercel.app/auth/callback`).

### 5. Finalize Oura Settings

1.  Copy your **Production Domain** from Vercel (e.g., `https://oura-api-test.vercel.app`).
2.  Go to [Oura Cloud Developer Console](https://cloud.ouraring.com/oauth/applications).
3.  Add the Redirect URI: `https://oura-api-test.vercel.app/auth/callback`.

## Testing

- Navigate to `https://oura-api-test.vercel.app/docs`.
- Follow the authentication flow.
- Test webhooks by registering `https://oura-api-test.vercel.app/webhook`.
