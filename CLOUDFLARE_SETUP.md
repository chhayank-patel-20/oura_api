# Deploying to Cloudflare Workers

Yes, you can run this Python FastAPI application on Cloudflare Workers!
It supports Python via Pyodide, allowing you to deploy serverless Python functions easily.

Since you want your team to access it via a **public URL** and to receive **webhooks** reliably, this is a great solution.

## Prerequisites

1.  **Node.js & npm** (You have v11.6.0 installed).
2.  **Cloudflare Account** (Free tier is sufficient).

## Deployment Steps

### 1. Install Wrangler

Wrangler is the CLI tool for Cloudflare Workers.

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

Authenticate the CLI with your account.

```bash
wrangler login
```

This will open a browser window to authorize.

### 3. Configuration

I have created a `wrangler.toml` file in the root directory. You need to review it.

**Important:**
For security, do **NOT** put your `OURA_CLIENT_SECRET` in the `wrangler.toml` file directly if you plan to commit this code. Instead, use secrets:

```bash
wrangler secret put OURA_CLIENT_SECRET
# Enter your secret when prompted
```

For the `OURA_CLIENT_ID`, you can either put it in `wrangler.toml` (if not sensitive) or use `wrangler secret put OURA_CLIENT_ID`.

### 4. Deploy

Run the deployment command:

```bash
wrangler deploy
```

### 5. Post-Deployment Setup

After deployment, Wrangler will output your Worker URL, e.g., `https://ouraphythonapi.your-subdomain.workers.dev`.

1.  **Update Oura App Settings**:
    - Go to the [Oura Cloud Developer Console](https://cloud.ouraring.com/oauth/applications).
    - Add the new Redirect URI: `https://ouraphythonapi.your-subdomain.workers.dev/auth/callback`
    - (Update your environment variable `OURA_REDIRECT_URI` if you haven't set it dynamically).

2.  **Webhooks**:
    - Your webhook URL will be: `https://ouraphythonapi.your-subdomain.workers.dev/webhook`
    - Register this URL in the Oura Console for real-time updates.

## Notes on Python in Workers

- Cloudflare Workers uses a Pyodide runtime.
- Most pure Python packages work.
- `FastAPI` is supported.
- If you encounter issues with `requests` (which is synchronous), consider switching to `httpx` or `aiohttp` for better performance in the async Worker environment, although `requests` is often patched in these environments.

## Alternative: Vercel (Recommended for simplicity)

If Cloudflare proves difficult, **Vercel** also supports Python FastAPI out of the box with zero config (just a `vercel.json`).
It also provides a public HTTPS URL and works great for webhooks.

To deploy on Vercel:

1.  `npm i -g vercel`
2.  `vercel` (follow prompts)
