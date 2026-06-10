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
            # 加入一点点颜色区分，金额大的用加粗
            report_html += f"""
            <li style="margin-bottom: 8px;">
                <span style="color: #555;">{service}</span>: 
                <strong style="color: #232f3e;">${amount:.2f}</strong>
            </li>"""
            
    return report_html if report_html else "<li><em>昨日无产生新费用。</em></li>"

def lambda_handler(event, context):
    expiry_date = datetime.strptime(CONFIG["expiry_date"], '%Y-%m-%d')
    days_remaining = (expiry_date - datetime.now()).days
    
    try:
        usage_details_html = get_billing_data_html()
        
        # 带有 AWS 品牌风格的 HTML 模板
        html_body = f"""
        <html>
        <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-top: 4px solid #ff9900; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="padding: 20px; background-color: #232f3e; color: #ffffff;">
                    <h2 style="margin: 0;">AWS 每日费用监控报告</h2>
                </div>
                
                <div style="padding: 30px;">
                    <h3 style="color: #232f3e; margin-top: 0;">账户额度概况</h3>
                    <div style="background-color: #fff8f0; border-left: 4px solid #ff9900; padding: 15px; margin-bottom: 20px;">
                        <p style="margin: 5px 0;"><strong>剩余抵扣额度:</strong> <span style="color: #d13212; font-size: 1.2em;">${CONFIG["credits_remaining"]:.2f}</span></p>
                        <p style="margin: 5px 0;"><strong>有效期剩余:</strong> {days_remaining} 天 (至 {CONFIG["expiry_date"]})</p>
                    </div>

                    <h3 style="color: #232f3e;">昨日费用明细</h3>
                    <ul style="list-style-type: none; padding: 0;">
                        {usage_details_html}
                    </ul>
                </div>
                
                <div style="padding: 15px; background-color: #f9f9f9; text-align: center; font-size: 12px; color: #888;">
                    此报告由 AWS Lambda 自动监控生成 | 建议定期登录 AWS 控制台查看明细
                </div>
            </div>
        </body>
        </html>
        """
        
        ses = boto3.client('ses', region_name='us-east-1')
        ses.send_email(
            Source=CONFIG["sender"],
            Destination={'ToAddresses': [CONFIG["recipient"]]},
            Message={
                'Subject': {'Data': 'AWS 每日费用监控报告'},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        
        return {"statusCode": 200, "body": "Report sent successfully"}

    except Exception as e:
        print(f"发送失败: {str(e)}")
        raise e