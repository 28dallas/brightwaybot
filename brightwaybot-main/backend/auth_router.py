from fastapi import APIRouter, HTTPException, Depends
from authlib.integrations.fastapi_oauth2 import OAuth2Token
from authlib.integrations.httpx_oauth2 import OAuth2Client
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback')

oauth = OAuth2Client(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_uri=GOOGLE_REDIRECT_URI,
    base_url='https://accounts.google.com/o/oauth2/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_url='https://www.googleapis.com/oauth2/v2/userinfo'
)

@router.get('/auth/google/login')
async def google_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="OAuth not configured")
    
    authorization_url, state = oauth.create_authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        scope=['openid', 'email', 'profile']
    )
    return {'authorization_url': authorization_url, 'state': state}

@router.get('/auth/google/callback')
async def google_callback(code: str, state: str):
    try:
        token = await oauth.fetch_token(
            'https://oauth2.googleapis.com/token',
            code=code
        )
        user_info = await oauth.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user = user_info.json()
        
        # Here you can save user to database or create session
        return {
            'access_token': token['access_token'],
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'picture': user.get('picture')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth callback failed: {str(e)}")
