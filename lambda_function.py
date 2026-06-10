import boto3
from datetime import datetime, timedelta

CONFIG = {
    "credits_remaining": 83.62,
    "expiry_date": "2026-11-30",
    "sender": "pengchao.ma6@gmail.com",       
    "recipient": "prometheus_0521@qq.com"          
}

def get_billing_data():
    ce = boto3.client('ce', region_name='us-east-1')
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
        if amount > 0:
            report.append(f"  - {service}: ${amount:.2f}")
            
    return "\n".join(report) if report else "  - no fees generated yesterday"

def lambda_handler(event, context):
    # calculate remaining days dynamicly 
    expiry_date = datetime.strptime(CONFIG["expiry_date"], '%Y-%m-%d')
    days_remaining = (expiry_date - datetime.now()).days
    
    try:
        usage_details = get_billing_data()
        
        email_body = f"""
您好，这是您的 AWS 每日费用监控报告：

【账户额度概况】
--------------------------
剩余抵扣额度: ${CONFIG["credits_remaining"]}
预计有效期剩余: {days_remaining} 天 (至 {CONFIG["expiry_date"]})

【昨日费用明细】
--------------------------
{usage_details}

--------------------------
此报告由 AWS Lambda 自动化监控生成。
"""
        
        ses = boto3.client('ses', region_name='us-east-1')
        ses.send_email(
            Source=CONFIG["sender"],
            Destination={'ToAddresses': [CONFIG["recipient"]]},
            Message={
                'Subject': {'Data': 'AWS 每日费用报告'},
                'Body': {'Text': {'Data': email_body}}
            }
        )
        
        return {"statusCode": 200, "body": "Report sent successfully"}

    except Exception as e:
        print(f"发送失败: {str(e)}")
        raise e