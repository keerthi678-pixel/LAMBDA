import boto3
import openpyxl
from openpyxl.styles import Font
import tempfile
import os

s3 = boto3.client('s3')
ec2 = boto3.client('ec2')

BUCKET_NAME = 'my-ec2-reports-bucket'  # 🔁 Replace with your actual bucket name

def lambda_handler(event, context):
    instances_info = []

    reservations = ec2.describe_instances()['Reservations']
    
    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            public_ip = instance.get('PublicIpAddress', 'N/A')
            username = 'ec2-user'
            password = 'YourSecurePassword123'  # Replace with your actual logic or secret

            instances_info.append([instance_id, public_ip, username, password])
    
    # Create Excel workbook
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "EC2 Instances"

    headers = ["Instance ID", "Public IP", "Username", "Password"]
    sheet.append(headers)
    
    # Bold headers
    for col in range(1, len(headers) + 1):
        sheet.cell(row=1, column=col).font = Font(bold=True)

    # Add instance data
    for row in instances_info:
        sheet.append(row)

    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        file_path = tmp.name
        workbook.save(file_path)

    # Upload to S3
    s3_key = "ec2-instance-details.xlsx"
    s3.upload_file(file_path, BUCKET_NAME, s3_key)

    os.remove(file_path)  # Clean up

    return {
        "statusCode": 200,
        "body": instances_info,
        "excel_s3_url": f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    }
