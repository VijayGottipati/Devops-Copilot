from django.urls import path
from .oauth_views import OAuthCallbackView
from .webhook_views import SlackWebhookView, DiscordWebhookView
from .video_ingestion import MeetingAnalysisView

urlpatterns = [
    path('auth/<str:provider>/callback/', OAuthCallbackView.as_view(), name='oauth_callback'),
    path('slack/events/', SlackWebhookView.as_view(), name='slack_events'),
    path('discord/events/', DiscordWebhookView.as_view(), name='discord_events'),
    path('video/analyze/', MeetingAnalysisView.as_view(), name='video_analyze'),
]
