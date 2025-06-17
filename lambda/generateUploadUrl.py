import os
import json
import boto3
import uuid
from botocore.client import Config

# ✅ Explicit region and signature version for stability
s3 = boto3.client(
    's3',
    region_name='us-east-1',
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = os.environ.get("BUCKET_NAME")

def lambda_handler(event, context):
    print("=== EVENT RECEIVED ===")
    print(json.dumps(event, indent=2))

    if event.get('httpMethod') == 'OPTIONS':
        print("Preflight OPTIONS request handled.")
        return {
            'statusCode': 200,
            'headers': cors_headers()
        }

    try:
        body = json.loads(event['body'])
        voice = body.get('voice', 'Joanna')
        email = body.get('email', 'example@example.com')
        ext = body.get('ext', 'pdf')

        file_id = str(uuid.uuid4())
        file_key = f"uploads/{file_id}___{voice}___{email}.{ext}"

        print("=== UPLOAD DETAILS ===")
        print(f"Voice: {voice}")
        print(f"Email: {email}")
        print(f"File extension: {ext}")
        print(f"Generated file key: {file_key}")

        url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': file_key
                # Not including ContentType for simplicity
            },
            ExpiresIn=300
        )

        print("Generated presigned URL successfully.")

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'uploadUrl': url,
                'fileId': file_id,
                'voice': voice,
                'email': email
            })
        }

    except Exception as e:
        print("❌ ERROR occurred while generating presigned URL")
        print(str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,OPTIONS',
        'Access-Control-Allow-Headers': '*'
    }
