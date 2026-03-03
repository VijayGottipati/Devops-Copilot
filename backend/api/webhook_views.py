from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .sqs_utils import push_to_queue

class SlackWebhookView(APIView):
    def post(self, request):
        payload = request.data
        
        # Slack URL verification payload handling
        if payload.get('type') == 'url_verification':
            return Response({'challenge': payload.get('challenge')}, status=status.HTTP_200_OK)
            
        # Push to SQS for async processing within 3s window
        if 'event' in payload:
            push_to_queue(payload, 'slack')
        
        # Immediate 200 OK to prevent Slack timeout
        return Response(status=status.HTTP_200_OK)

class DiscordWebhookView(APIView):
    def post(self, request):
        payload = request.data
        
        # Free-Tier Error Monitoring hack using Discord channels as log aggregators
        # If payload originates from our specific "#server-logs" webhook structure
        if payload.get('content') and "ERROR" in payload.get('content'):
            push_to_queue({
                "type": "error_log",
                "message": payload.get('content'),
                "raw_payload": payload
            }, "discord_logs")
        else:
            # Push to SQS for standard async processing
            push_to_queue(payload, 'discord')
        
        # Immediate 204 No Content for Discord webhook handling
        return Response(status=status.HTTP_204_NO_CONTENT)
