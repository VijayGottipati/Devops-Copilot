import json
import time
from django.core.management.base import BaseCommand
from api.sqs_utils import get_sqs_client
import os

class Command(BaseCommand):
    help = 'Runs the SQS consumer to process webhooks asynchronously using LangGraph'

    def handle(self, *args, **options):
        queue_url = os.environ.get('AWS_SQS_QUEUE_URL')
        if not queue_url:
            self.stdout.write(self.style.ERROR('AWS_SQS_QUEUE_URL is not set.'))
            return

        client = get_sqs_client()
        self.stdout.write(self.style.SUCCESS('Starting SQS Consumer...'))

        while True:
            try:
                response = client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20
                )

                messages = response.get('Messages', [])
                for message in messages:
                    receipt_handle = message['ReceiptHandle']
                    body = json.loads(message['Body'])
                    
                    self.stdout.write(f"Processing event from {body.get('provider')}")
                    
                    # NOTE: Here we will invoke the LangGraph workflow shortly.
                    self.process_with_langgraph(body)
                    
                    client.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=receipt_handle
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error polling SQS: {e}"))
                time.sleep(5)
                
    def process_with_langgraph(self, event_data):
        from api.agents import invoke_swarm
        
        # In a real payload we would extract the Slack/Discord message text
        # For now, we simulate pulling the relevant 'text' from the event_data JSON tree
        message_text = event_data.get('payload', {}).get('event', {}).get('text', "Analyze this request")
        
        provider = event_data.get('provider')
        self.stdout.write(f"Triggering LangGraph Swarm for {provider} message: {message_text}")
        
        response = invoke_swarm(message_text)
        self.stdout.write(self.style.SUCCESS(f"Agent Response: {response}"))
        
        # Here we would use the Slack/Discord APIs or Bot SDKs to reply back to the channel.
