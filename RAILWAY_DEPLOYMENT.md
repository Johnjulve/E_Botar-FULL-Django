# Railway Deployment Guide for E-Botar

This guide explains how to deploy E-Botar to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Your project repository connected to Railway
3. A PostgreSQL database service on Railway

## Automatic Configuration

The project is now configured to automatically detect Railway environment and adjust settings accordingly:

- **Database**: Automatically uses PostgreSQL when `DATABASE_URL` is present (Railway provides this)
- **Static Files**: Uses WhiteNoise for efficient static file serving
- **Security**: Production security settings enabled on Railway
- **Debug Mode**: Automatically disabled on Railway

## Required Environment Variables

Set these in your Railway project settings:

### Required Variables

1. **SECRET_KEY** (Required)
   - Generate a new secret key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - Or use: `openssl rand -base64 32`
   - **Important**: Never commit this to version control!

2. **DATABASE_URL** (Auto-provided by Railway)
   - Railway automatically provides this when you add a PostgreSQL service
   - No manual configuration needed

3. **DEBUG** (Optional, defaults to False on Railway)
   - Set to `False` for production
   - Set to `True` only for debugging (not recommended in production)

### Optional Variables

4. **ALLOWED_HOSTS** (Optional)
   - Comma-separated list of allowed hosts
   - Railway domain is automatically added if `RAILWAY_PUBLIC_DOMAIN` is set

5. **CUSTOM_DOMAIN** (Optional)
   - Your custom domain if you're using one
   - Example: `yourdomain.com`

6. **SECURE_SSL_REDIRECT** (Optional, defaults to False)
   - Set to `True` to force HTTPS redirects

## Deployment Steps

### 1. Add PostgreSQL Database

1. In your Railway project, click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically create a `DATABASE_URL` environment variable

### 2. Set Environment Variables

1. Go to your Railway project → Settings → Variables
2. Add the following variables:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
```

### 3. Deploy

1. Railway will automatically detect the `Procfile` and deploy
2. The deployment will:
   - Run migrations automatically
   - Collect static files
   - Start the Gunicorn server

### 4. Verify Deployment

1. Check the Railway logs for any errors
2. Visit your Railway-provided domain
3. Test the application functionality

## Database Migration

The `Procfile` automatically runs migrations on each deployment. If you need to run migrations manually:

```bash
railway run python manage.py migrate
```

## Static Files

Static files are automatically collected during deployment. If you need to collect them manually:

```bash
railway run python manage.py collectstatic --noinput
```

## Local Development vs Railway

The settings automatically detect the environment:

- **Local Development**: Uses SQLite, DEBUG=True, relaxed security
- **Railway Production**: Uses PostgreSQL, DEBUG=False, production security enabled

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is set in Railway environment variables
- Check that PostgreSQL service is running
- Verify database credentials in Railway dashboard

### Static Files Not Loading

- Ensure `collectstatic` ran successfully (check deployment logs)
- Verify `STATIC_ROOT` directory exists
- Check WhiteNoise middleware is in `MIDDLEWARE` list

### CSRF Errors

- Verify `CSRF_TRUSTED_ORIGINS` includes your Railway domain
- Check that `RAILWAY_PUBLIC_DOMAIN` is set correctly
- If using custom domain, add it to `CUSTOM_DOMAIN` environment variable

### Email Verification Issues

- Configure email backend in settings (SMTP settings)
- For production, use a service like SendGrid, Mailgun, or AWS SES
- Set email-related environment variables

## Security Checklist

- [ ] `SECRET_KEY` is set and secure
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] HTTPS is enabled (Railway provides this automatically)
- [ ] Database credentials are secure
- [ ] No sensitive data in code or logs

## Support

For Railway-specific issues, check:
- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

For E-Botar-specific issues, refer to the main README.md

