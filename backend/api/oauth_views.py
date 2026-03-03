import os
import requests
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
import urllib.parse
from .models import OAuthToken, Project
from django.conf import settings

FRONTEND_URL = getattr(settings, "CORS_ALLOWED_ORIGINS", ["http://localhost:4200"])[0]

class OAuthLoginView(APIView):
    def get(self, request, provider):
        state = request.GET.get('project_id', '1') # Pass project ID in state
        
        if provider == 'gmail':
            client_id = os.environ.get('GMAIL_CLIENT_ID')
            redirect_uri = os.environ.get('GMAIL_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/gmail/callback/')
            scope = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send"
            url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}&access_type=offline&prompt=consent"
            return redirect(url)
            
        elif provider == 'github':
            client_id = os.environ.get('GITHUB_CLIENT_ID')
            redirect_uri = os.environ.get('GITHUB_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/github/callback/')
            scope = "repo read:user user:email"
            url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"
            return redirect(url)
            
        elif provider == 'slack':
            client_id = os.environ.get('SLACK_CLIENT_ID')
            redirect_uri = os.environ.get('SLACK_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/slack/callback/')
            scope = "app_mentions:read,channels:history,chat:write,groups:history,im:history,mpim:history"
            url = f"https://slack.com/oauth/v2/authorize?client_id={client_id}&scope={scope}&redirect_uri={redirect_uri}&state={state}"
            return redirect(url)
            
        elif provider == 'discord':
            client_id = os.environ.get('DISCORD_CLIENT_ID')
            redirect_uri = os.environ.get('DISCORD_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/discord/callback/')
            scope = "webhook.incoming responses.read"
            url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}"
            return redirect(url)
            
        return Response({"error": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)

class OAuthCallbackView(APIView):
    def get(self, request, provider):
        code = request.GET.get('code')
        # project_id should be passed in the state parameter
        state = request.GET.get('state', '1') # Default project ID 1 for MVP
        
        if not code:
            return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            project, _ = Project.objects.get_or_create(id=int(state), defaults={"name": "Default Project"})
        except ValueError:
            return Response({"error": "Invalid project ID in state"}, status=status.HTTP_400_BAD_REQUEST)

        if provider == 'slack':
            return self.handle_slack(code, project)
        elif provider == 'discord':
            return self.handle_discord(code, project)
        elif provider == 'gmail':
            return self.handle_gmail(code, project)
        elif provider == 'github':
            return self.handle_github(code, project)
        else:
            return redirect(f"{FRONTEND_URL}?status=error&message=Unsupported+provider")

    def handle_slack(self, code, project):
        client_id = os.environ.get('SLACK_CLIENT_ID')
        client_secret = os.environ.get('SLACK_CLIENT_SECRET')
        redirect_uri = os.environ.get('SLACK_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/slack/callback/')
        
        response = requests.post('https://slack.com/api/oauth.v2.access', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        })
        
        data = response.json()
        if not data.get('ok'):
            return redirect(f"{FRONTEND_URL}?status=error&message=Slack+OAuth+Failed")
            
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        
        self.save_token(project, 'slack', access_token, refresh_token, expires_at)
        return redirect(f"{FRONTEND_URL}?status=success&provider=slack")

    def handle_discord(self, code, project):
        client_id = os.environ.get('DISCORD_CLIENT_ID')
        client_secret = os.environ.get('DISCORD_CLIENT_SECRET')
        redirect_uri = os.environ.get('DISCORD_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/discord/callback/')
        
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        response = requests.post('https://discord.com/api/oauth2/token', data=data, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        data = response.json()
        if 'error' in data:
            return redirect(f"{FRONTEND_URL}?status=error&message=Discord+OAuth+Failed")
            
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        
        self.save_token(project, 'discord', access_token, refresh_token, expires_at)
        return redirect(f"{FRONTEND_URL}?status=success&provider=discord")

    def handle_gmail(self, code, project):
        client_id = os.environ.get('GMAIL_CLIENT_ID')
        client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
        redirect_uri = os.environ.get('GMAIL_REDIRECT_URI', 'https://devops-copilot-gc91.onrender.com/api/auth/gmail/callback/')
        
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        response = requests.post('https://oauth2.googleapis.com/token', data=data)
        data = response.json()
        
        if 'error' in data:
            return redirect(f"{FRONTEND_URL}?status=error&message=Gmail+OAuth+Failed")
            
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        
        self.save_token(project, 'gmail', access_token, refresh_token, expires_at)
        return redirect(f"{FRONTEND_URL}?status=success&provider=gmail")

    def handle_github(self, code, project):
        client_id = os.environ.get('GITHUB_CLIENT_ID')
        client_secret = os.environ.get('GITHUB_CLIENT_SECRET')
        
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code
        }
        
        response = requests.post('https://github.com/login/oauth/access_token', data=data, headers={'Accept': 'application/json'})
        data = response.json()
        
        if 'error' in data:
            return redirect(f"{FRONTEND_URL}?status=error&message=GitHub+OAuth+Failed")
            
        access_token = data.get('access_token')
        
        self.save_token(project, 'github', access_token, None, None)
        return redirect(f"{FRONTEND_URL}?status=success&provider=github")
        
    def save_token(self, project, provider, access_token, refresh_token, expires_at):
        OAuthToken.objects.update_or_create(
            project=project,
            provider=provider,
            defaults={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at
            }
        )
