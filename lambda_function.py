import boto3
import os

def lambda_handler(event, context):
    ses = boto3.client('ses')
    print("准备发送邮件...")
    try:
        ses.send_email(
            Source=os.environ['SENDER'],
            Destination={'ToAddresses': [os.environ['RECIPIENT']]},
            Message={
                'Subject': {'Data': '定时通知'},
                'Body': {'Text': {'Data': '这是一条来自 Lambda 的定时测试消息。'}}
            }
        )
        print("邮件已成功发送")
    except Exception as e:
        print(f"发送失败: {str(e)}")
        raise e