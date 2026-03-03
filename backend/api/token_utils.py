import os
import requests
from django.utils import timezone
from datetime import timedelta
from .models import OAuthToken

def refresh_token_if_needed(project, provider):
    token = OAuthToken.objects.filter(project=project, provider=provider).first()
    if not token or not token.expires_at:
        return token
        
    # Refresh if within 5 minutes of expiring
    if token.expires_at <= timezone.now() + timedelta(minutes=5):
        if provider == 'gmail':
            token = refresh_gmail_token(token)
        # Note: Discord user access tokens expire, but since we are handling webhooks, 
        # we generally interact via Bot Tokens or specific webhook URLs which stay valid.
        # Slack bot tokens don't typically expire unless explicitly rotated.
            
    return token

def refresh_gmail_token(token):
    client_id = os.environ.get('GMAIL_CLIENT_ID')
    client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
    
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': token.refresh_token,
        'grant_type': 'refresh_token'
    })
    
    data = response.json()
    if 'access_token' in data:
        token.access_token = data['access_token']
        if 'expires_in' in data:
            token.expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
        token.save()
        
    return token
