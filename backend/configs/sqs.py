import boto3
import os
from dotenv import load_dotenv
load_dotenv()


class SQSClient:
    def __init__(self):
        self.client = boto3.client(
            'sqs',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
    def send_message(self,message_body:str):
        
        try:
            self.client.send_message(
                QueueUrl=os.getenv("SQS_URL"),
                MessageBody=message_body
            )
            print("Message sent to SQS successfully")
        except Exception as e:
            print("Error sending message to SQS:", e)
            
    def receive_message(self,max_messages:int=1):
        
        try:
            response = self.client.receive_message(
                QueueUrl=os.getenv("SQS_URL"),
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20
            )
            return response.get('Messages', [])
        except Exception as e:
            print("Error receiving messages from SQS:", e)
            return []
        
    def delete_message(self,receipt_handle:str):
        
        try:
            self.client.delete_message(
                QueueUrl=os.getenv("SQS_URL"),
                ReceiptHandle=receipt_handle
            )
            print("Message deleted from SQS successfully")
        except Exception as e:
            print("Error deleting message from SQS:", e)
            
        
    
sqs_client=SQSClient()
    
    