import boto3
from datetime import datetime, timedelta

# --- 集中配置区域 ---
CONFIG = {
    "credits_remaining": 83.62,
    "expiry_date": "2026-11-30",
    "sender": "pengchao.ma6@gmail.com",       
    "recipient": "prometheus_0521@qq.com"          
}

def get_billing_data_html():
    """获取账单并返回 HTML 列表格式"""
    ce = boto3.client('ce', region_name='us-east-1')
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    report_html = ""
    for result in response['ResultsByTime'][0]['Groups']:
        service = result['Keys'][0]
        amount = float(result['Metrics']['UnblendedCost']['Amount'])
        if amount > 0:
            report_html += f"<li><strong>{service}</strong>: ${amount:.2f}</li>"
            
    return report_html if report_html else "<li>昨日无产生新费用。</li>"

def lambda_handler(event, context):
    expiry_date = datetime.strptime(CONFIG["expiry_date"], '%Y-%m-%d')
    days_remaining = (expiry_date - datetime.now()).days
    
    try:
        usage_details_html = get_billing_data_html()
        
        # HTML 邮件模板
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #333; }}
                .card {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; max-width: 500px; }}
                .header {{ color: #232f3e; border-bottom: 2px solid #ff9900; }}
                .summary {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; margin: 15px 0; }}
                ul {{ padding-left: 20px; }}
                li {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2 class="header">AWS 每日费用监控报告</h2>
                <div class="summary">
                    <p><strong>剩余抵扣额度:</strong> ${CONFIG["credits_remaining"]:.2f}</p>
                    <p><strong>预计有效期剩余:</strong> {days_remaining} 天 (至 {CONFIG["expiry_date"]})</p>
                </div>
                <h3>昨日费用明细:</h3>
                <ul>{usage_details_html}</ul>
                <hr>
                <p style="font-size: 12px; color: #777;">此报告由 AWS Lambda 自动化监控生成。</p>
            </div>
        </body>
        </html>
        """
        
        ses = boto3.client('ses', region_name='us-east-1')
        ses.send_email(
            Source=CONFIG["sender"],
            Destination={'ToAddresses': [CONFIG["recipient"]]},
            Message={
                'Subject': {'Data': 'AWS 每日费用报告'},
                'Body': {'Html': {'Data': html_body}} # 关键：将 Body 设为 Html
            }
        )
        
        return {"statusCode": 200, "body": "Report sent successfully"}

    except Exception as e:
        print(f"发送失败: {str(e)}")
        raise e