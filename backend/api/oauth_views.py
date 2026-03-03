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
        else:
            return Response({"error": "Unsupported provider"}, status=status.HTTP_400_BAD_REQUEST)

    def handle_slack(self, code, project):
        client_id = os.environ.get('SLACK_CLIENT_ID')
        client_secret = os.environ.get('SLACK_CLIENT_SECRET')
        redirect_uri = os.environ.get('SLACK_REDIRECT_URI', 'http://localhost:8000/api/auth/slack/callback/')
        
        response = requests.post('https://slack.com/api/oauth.v2.access', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri
        })
        
        data = response.json()
        if not data.get('ok'):
            return Response({"error": data.get('error')}, status=status.HTTP_400_BAD_REQUEST)
            
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        
        self.save_token(project, 'slack', access_token, refresh_token, expires_at)
        return Response({"status": "Slack connected successfully"})

    def handle_discord(self, code, project):
        client_id = os.environ.get('DISCORD_CLIENT_ID')
        client_secret = os.environ.get('DISCORD_CLIENT_SECRET')
        redirect_uri = os.environ.get('DISCORD_REDIRECT_URI', 'http://localhost:8000/api/auth/discord/callback/')
        
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
            return Response({"error": data.get('error_description', data.get('error'))}, status=status.HTTP_400_BAD_REQUEST)
            
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        
        self.save_token(project, 'discord', access_token, refresh_token, expires_at)
        return Response({"status": "Discord connected successfully"})

    def handle_gmail(self, code, project):
        client_id = os.environ.get('GMAIL_CLIENT_ID')
        client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
        redirect_uri = os.environ.get('GMAIL_REDIRECT_URI', 'http://localhost:8000/api/auth/gmail/callback/')
        
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
            return Response({"error": data.get('error_description', data.get('error'))}, status=status.HTTP_400_BAD_REQUEST)
            
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in')
        expires_at = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        
        self.save_token(project, 'gmail', access_token, refresh_token, expires_at)
        return Response({"status": "Gmail connected successfully"})
        
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
