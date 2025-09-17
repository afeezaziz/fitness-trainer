# Google OAuth Setup Guide

## Step 1: Go to Google Cloud Console

1. Open your web browser and navigate to: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Sign in with your Google account
3. If prompted, agree to the terms of service

## Step 2: Create a New Project

1. At the top of the page, click the project dropdown (might say "Select a project")
2. Click "NEW PROJECT" or "CREATE PROJECT"
3. Enter a project name: `Fitness Trainer App`
4. Click "CREATE"

## Step 3: Enable OAuth 2.0 APIs

1. In the navigation menu (☰), go to **APIs & Services > Library**
2. Search for "Google Identity Toolkit API" and enable it
3. Search for "People API" and enable it
4. These APIs are needed for user authentication and profile information

## Step 4: Create OAuth 2.0 Credentials

1. In the navigation menu, go to **APIs & Services > OAuth consent screen**
2. Select **External** for user type
3. Click "CREATE"

### Configure OAuth Consent Screen:

**App information:**
- App name: `Fitness Trainer`
- User support email: `your-email@gmail.com` (use your email)
- App logo: (optional) you can upload a logo later
- App domain: Leave blank for now

**Developer contact information:**
- Add your email address

**Scopes:**
- Click "ADD OR REMOVE SCOPES"
- Search for and select:
  - `../auth/userinfo.email`
  - `../auth/userinfo.profile`
- Click "UPDATE"

**Test users:**
- Click "ADD USERS"
- Add your email address as a test user (required during development)

**Summary:**
- Click "BACK TO DASHBOARD"

## Step 5: Create Credentials

1. In the navigation menu, go to **APIs & Services > Credentials**
2. Click "+ CREATE CREDENTIALS" and select "OAuth client ID"

**Application type:**
- Select **Web application**

**Name:**
- Enter: `Fitness Trainer Web App`

**Authorized redirect URIs:**
- Click "+ ADD URI"
- Enter: `http://localhost:8081/authorize`
- Enter: `http://127.0.0.1:8081/authorize`

**Restrictions:**
- Leave JavaScript origins empty for local development

3. Click "CREATE"

## Step 6: Get Your Credentials

After creating the credentials, you'll see:
- **Client ID**: A long string starting with numbers
- **Client Secret**: A longer random string

**IMPORTANT:** Copy both values immediately as you won't be able to see the client secret again.

## Step 7: Configure Your App

1. Create a `.env` file in your project root:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your credentials:
```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here

# Flask Configuration
SECRET_KEY=a-random-secret-key-for-security
FLASK_ENV=development
```

## Step 8: Test Your Setup

1. Restart your Flask app:
```bash
pkill -f "python run.py"
uv run python run.py
```

2. Open your browser to: `http://localhost:8081`

3. Click "Login with Google" and test the authentication flow

## Troubleshooting

### Common Issues:

**Redirect URI mismatch error:**
- Make sure the redirect URI in Google Console exactly matches `http://localhost:8081/authorize`
- Include both `localhost` and `127.0.0.1` versions

**Invalid client error:**
- Double-check your Client ID and Client Secret in the `.env` file
- Make sure there are no extra spaces or typos

**Access not configured error:**
- Go back to OAuth consent screen and make sure you're added as a test user
- Ensure you've enabled the required APIs

**Port already in use:**
- Change the port in `run.py` if 8081 is being used by another application

## Production Deployment

When you're ready to deploy to production:

1. Go back to Google Cloud Console
2. Update the OAuth consent screen:
   - Change publishing status to "In production"
   - Add your domain to authorized domains
   - Update redirect URIs to your production URL (e.g., `https://yourapp.com/authorize`)

3. In your production environment:
   - Set environment variables instead of using `.env` file
   - Use a proper secret key generation method

## Security Notes

- Never commit your `.env` file to version control
- Use strong, randomly generated secrets in production
- Regularly rotate your OAuth client secret
- Monitor your OAuth usage in Google Cloud Console