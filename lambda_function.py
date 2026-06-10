import boto3
import os

def lambda_handler(event, context):
    ses = boto3.client('ses')
    print("Preparing to send email...")
    try:
        ses.send_email(
            Source=os.environ['SENDER'],
            Destination={'ToAddresses': [os.environ['RECIPIENT']]},
            Message={
                'Subject': {'Data': 'AWS payment notification'},
                'Body': {'Text': {'Data': 'Hello , Your need to pay your credit card immedately!!'}}
            }
        )
        print("email sent successfully!")
    except Exception as e:
        print(f"failed to send: {str(e)}")
        raise e