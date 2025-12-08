# 🚀 Railway Deployment Troubleshooting Guide

## 🐛 Current Issue: "pip: command not found"

### ✅ Solutions Implemented:

1. **Simplified nixpacks.toml** - Removed complex configuration that might confuse Railway's build system
2. **Added .python-version** - Explicitly tells Railway to use Python 3.11
3. **Updated railway.toml** - Better environment variable configuration
4. **Created Dockerfile** - Alternative deployment method if nixpacks fails

### 🔄 Deployment Options:

#### Option 1: Use Simplified Nixpacks (Recommended)
The updated `nixpacks.toml` should resolve the pip issue:
```toml
[variables]
PYTHON_VERSION = "3.11"

[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn rejlers_api.wsgi:application --bind 0.0.0.0:$PORT"
```

#### Option 2: Use Dockerfile
If nixpacks continues to fail, Railway can use the Dockerfile:
1. In Railway Dashboard → Settings → Build
2. Change "Builder" from "Nixpacks" to "Dockerfile"
3. Redeploy

#### Option 3: Remove nixpacks.toml Entirely
Railway auto-detects Python projects. Sometimes removing nixpacks.toml helps:
1. Temporarily rename `nixpacks.toml` to `nixpacks.toml.backup`
2. Let Railway auto-detect the Python environment
3. Redeploy

### 🔧 Environment Variables Required in Railway:

```bash
# Database (Railway provides this)
DATABASE_URL=postgresql://...

# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=rejlers_api.production_settings

# AWS Credentials
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_DEFAULT_REGION=eu-north-1
AWS_STORAGE_BUCKET_NAME=rejlers-erp-storage

# OpenAI
OPENAI_API_KEY=your-openai-key

# Security
ALLOWED_HOSTS=*.railway.app,*.up.railway.app,localhost
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app
```

### 🚨 Common Railway Issues & Fixes:

#### 1. Build Timeout
- Reduce dependencies in requirements.txt
- Use `--no-cache-dir` flag in pip installs

#### 2. Memory Issues
- Reduce Gunicorn workers from 4 to 2
- Add memory limits in railway.toml

#### 3. Static Files Not Found
- Ensure WhiteNoise is in MIDDLEWARE
- Check STATIC_ROOT and STATIC_URL settings

#### 4. Database Connection Issues
- Use production_settings.py with proper SSL settings
- Ensure DATABASE_URL is properly configured

### 📊 Monitoring & Health Checks

Railway will monitor these endpoints:
- Health Check: `/api/v1/health/`
- Ready Check: `/api/v1/ready/`

### 🔍 Debugging Steps:

1. **Check Railway Logs:**
   ```bash
   railway logs
   ```

2. **Test Local Build:**
   ```bash
   python manage.py collectstatic --noinput
   gunicorn rejlers_api.wsgi:application --bind 0.0.0.0:8000
   ```

3. **Verify Requirements:**
   ```bash
   pip freeze > requirements-freeze.txt
   # Compare with requirements.txt
   ```

### 💡 Quick Fixes to Try:

1. **Remove nixpacks.toml temporarily**
2. **Add to requirements.txt:**
   ```
   setuptools>=65.0.0
   wheel>=0.37.0
   ```
3. **Update Procfile:**
   ```
   web: python -m gunicorn rejlers_api.wsgi:application --bind 0.0.0.0:$PORT
   ```

### 📞 Support

If issues persist:
- Check Railway Community: https://help.railway.app/
- Railway Discord: https://discord.gg/railway
- Project Contact: mohammed.agra@rejlers.com