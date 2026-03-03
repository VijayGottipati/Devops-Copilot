from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

class WebhookSQSTests(TestCase):

    @patch('api.webhook_views.push_to_queue')
    def test_discord_webhook_pushes_to_sqs(self, mock_push):
        """Test that Discord payloads are sent to SQS and return immediately."""
        url = reverse('discord_events')
        payload = {"content": "Test discord message"}
        
        response = self.client.post(url, payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 204)
        mock_push.assert_called_once_with(payload, 'discord')

    @patch('api.webhook_views.push_to_queue')
    def test_discord_webhook_error_log_interception(self, mock_push):
        """Test the Optimizer Agent's #server-logs interception route."""
        url = reverse('discord_events')
        payload = {"content": "CRITICAL ERROR: Connection timeout in API."}
        
        response = self.client.post(url, payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 204)
        # Should push to the specific 'discord_logs' queue type for the Optimizer
        mock_push.assert_called_once()
        call_args = mock_push.call_args[0]
        self.assertEqual(call_args[1], 'discord_logs')
        self.assertEqual(call_args[0]['type'], 'error_log')

    @patch('api.webhook_views.push_to_queue')
    def test_slack_webhook_verification(self, mock_push):
        """Test Slack's initial URL verification challenge."""
        url = reverse('slack_events')
        payload = {"type": "url_verification", "challenge": "abc123xyz"}
        
        response = self.client.post(url, payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['challenge'], "abc123xyz")
        mock_push.assert_not_called()

    @patch('api.webhook_views.push_to_queue')
    def test_slack_webhook_event_push(self, mock_push):
        """Test standard Slack events trigger SQS push."""
        url = reverse('slack_events')
        payload = {
            "type": "event_callback",
            "event": {"type": "message", "text": "Hello Copilot"}
        }
        
        response = self.client.post(url, payload, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_push.assert_called_once_with(payload, 'slack')
