# Render Deployment Instructions

## Quick Fix for Your Render Deployment

Your application is configured to work on both localhost and Render. Follow these steps to fix the Render deployment:

### Step 1: Add Environment Variable on Render

1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your service: **smartassist-chatbot-platform**
3. Click on **"Environment"** in the left sidebar
4. Click **"Add Environment Variable"**
5. Add the following variable:
   - **Key**: `RENDER`
   - **Value**: `True`

### Step 2: Verify Other Environment Variables

Make sure these environment variables are set on Render:

| Variable | Value | Notes |
|----------|-------|-------|
| `DEBUG` | `False` | **Important**: Must be False for production |
| `RENDER` | `True` | **New**: Enables HTTPS security |
| `SECRET_KEY` | `<your-secret-key>` | Generate a secure random key |
| `ALLOWED_HOSTS` | `smartassist-chatbot-platform.onrender.com` | Your Render domain |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | Your API key |
| `DB_ENGINE` | `django.db.backends.postgresql` | If using PostgreSQL |
| `DATABASE_URL` | `<auto-set-by-render>` | Automatically set if using Render PostgreSQL |

### Step 3: Deploy the Changes

After adding the environment variable:

1. **Push your code** to GitHub (if using auto-deploy):
   ```bash
   git add .
   git commit -m "Fix Render deployment settings"
   git push origin main
   ```

2. **Or manually deploy** from Render dashboard:
   - Click "Manual Deploy" → "Deploy latest commit"

### Step 4: Verify Deployment

Once deployed, test these URLs:
- ✅ https://smartassist-chatbot-platform.onrender.com/
- ✅ https://smartassist-chatbot-platform.onrender.com/login/
- ✅ https://smartassist-chatbot-platform.onrender.com/register/

## How It Works

The updated `settings.py` now detects the environment:

```python
IS_RENDER = os.getenv('RENDER', 'False') == 'True'

if not DEBUG and IS_RENDER:
    # Enable HTTPS-only security for Render
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # ... other HTTPS settings
elif not DEBUG:
    # Running locally with DEBUG=False - basic security only
    SECURE_BROWSER_XSS_FILTER = True
```

- **On Render**: `RENDER=True` → Full HTTPS security enabled
- **On localhost**: `RENDER` not set → HTTPS security disabled, works with HTTP

## Troubleshooting

### If you still get 500 errors on Render:

1. **Check Render logs**:
   - Go to Render dashboard → Your service → "Logs"
   - Look for error messages

2. **Verify environment variables**:
   - Make sure `RENDER=True` is set
   - Make sure `DEBUG=False` is set

3. **Check static files**:
   ```bash
   # Run this before deploying
   python manage.py collectstatic --noinput
   ```

4. **Database migrations**:
   - The `Procfile` already runs migrations: `release: python manage.py migrate`

## Git Commands to Deploy

```bash
# Stage all changes
git add .

# Commit with a message
git commit -m "Fix Render deployment - add RENDER env detection"

# Push to GitHub (triggers auto-deploy on Render)
git push origin main
```

## Summary

✅ **Localhost**: Works with HTTP (no HTTPS required)  
✅ **Render**: Works with HTTPS (full security enabled)  
✅ **Both environments**: Properly configured

Just add `RENDER=True` to your Render environment variables and redeploy!
