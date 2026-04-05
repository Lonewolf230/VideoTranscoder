import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError,BotoCoreError
load_dotenv()


class SQSClient:
    def __init__(self):
        self.region_name=os.getenv("AWS_REGION")
        self.aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        self.queue_url=os.getenv("SQS_URL")
        self.client = boto3.client(
            'sqs',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        
    def send_message(self,message_body:str):
        
        try:
            self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body,
            )
            print("Message sent to SQS successfully")
        except (ClientError,BotoCoreError) as e:
            print("Error sending message to SQS:", e)
            raise Exception("Failed to send message") from e
            
    def receive_message(self,max_messages:int=1):
        
        try:
            response = self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20,
                VisibilityTimeout=900
            )
            return response.get('Messages', [])
        except Exception as e:
            print("Error receiving messages from SQS:", e)
            return []
        
    def delete_message(self,receipt_handle:str):
        
        try:
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            print("Message deleted from SQS successfully")
        except Exception as e:
            print("Error deleting message from SQS:", e)
            raise
            
        
    
sqs_client=SQSClient()
    
    