import boto3
import os
from datetime import datetime, timedelta

def get_billing_data():
    """从 Cost Explorer 获取过去一天的服务花费"""
    ce = boto3.client('ce', region_name='us-east-1')
    
    # 获取昨天到今天的日期（AWS 账单有延迟，建议查昨天）
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    report = []
    for result in response['ResultsByTime'][0]['Groups']:
        service = result['Keys'][0]
        amount = float(result['Metrics']['UnblendedCost']['Amount'])
        if amount > 0: # 只显示有花费的服务
            report.append(f"  - {service}: ${amount:.2f}")
            
    return "\n".join(report) if report else "  - 没有产生新的费用。"

def lambda_handler(event, context):
    # 你的账户基础信息（建议后续可以通过环境变量动态管理）
    credits_remaining = 83.62
    days_remaining = 174
    
    try:
        # 1. 获取账单明细
        usage_details = get_billing_data()
        
        # 2. 构建邮件正文
        email_body = f"""
您好，这是您的 AWS 每日费用监控报告：

【账户额度概况】
--------------------------
剩余抵扣额度 (Credits): ${credits_remaining}
预计有效期剩余: {days_remaining} 天

【昨日费用明细】
--------------------------
{usage_details}

--------------------------
请定期检查您的 AWS 控制台以获取最准确的实时信息。
"""
        
        # 3. 发送邮件
        ses = boto3.client('ses', region_name='us-east-1')
        ses.send_email(
            Source=os.environ['SENDER'],
            Destination={'ToAddresses': [os.environ['RECIPIENT']]},
            Message={
                'Subject': {'Data': 'AWS 每日费用报告'},
                'Body': {'Text': {'Data': email_body}}
            }
        )
        
        print("邮件已成功发送！")
        return {"statusCode": 200, "body": "Report sent successfully"}

    except Exception as e:
        print(f"发送失败: {str(e)}")
        raise e