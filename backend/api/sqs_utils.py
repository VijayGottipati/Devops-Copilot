import os
import json
import boto3

def get_sqs_client():
    return boto3.client(
        'sqs',
        region_name=os.environ.get('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

def push_to_queue(payload, provider):
    queue_url = os.environ.get('AWS_SQS_QUEUE_URL')
    if not queue_url:
        print("Warning: AWS_SQS_QUEUE_URL not set. In production, this drops the payload.")
        return False
        
    client = get_sqs_client()
    try:
        response = client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'provider': provider,
                'payload': payload
            })
        )
        return response.get('MessageId') is not None
    except Exception as e:
        print(f"Error pushing to SQS: {e}")
        return False
