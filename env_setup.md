# Environment Variables Setup

This project uses environment variables to store sensitive information like API keys and secrets.

## Local Development

1. Create a `.env` file in the root directory of the project
2. Add the following variables to the file:

```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

3. Replace the placeholder values with your actual credentials

## Loading Environment Variables

The application loads these environment variables automatically through Django's settings.py.

For production deployment, set these environment variables according to your hosting platform's instructions:

- Heroku: Set through the dashboard or using `heroku config:set VARIABLE=value`
- Docker: Include in your docker-compose.yml or use Docker secrets
- VPS/Server: Set in your server environment or in the WSGI configuration

## Obtaining Google OAuth Credentials

To get your Google OAuth credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Set the application type as "Web application"
6. Add authorized redirect URIs:
   - For local development: `http://127.0.0.1:8000/accounts/google/login/callback/`
   - For production: `https://yourdomain.com/accounts/google/login/callback/`
7. Copy the generated Client ID and Client Secret to your .env file 