import boto3
import os
import uuid
from urllib.parse import unquote_plus
from PyPDF2 import PdfReader
import docx2txt

s3 = boto3.client('s3')
polly = boto3.client('polly')
ses = boto3.client('ses')


BUCKET_NAME = os.environ.get("BUCKET_NAME")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")


def extract_text(bucket, key):
    tmp_path = f"/tmp/{os.path.basename(key)}"
    s3.download_file(bucket, key, tmp_path)

    if key.endswith('.pdf'):
        reader = PdfReader(tmp_path)
        return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    elif key.endswith('.docx'):
        return docx2txt.process(tmp_path)
    return ""


def send_email(recipient, audio_url):
    try:
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 20px;">
          <div style="max-width: 600px; margin: auto; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <h2 style="color: #333;">🎧 Your Audio is Ready!</h2>
            <p>Hi there 👋,</p>
            <p>Your document has been successfully converted to audio.</p>
            <p>
              <a href="{audio_url}" style="display: inline-block; padding: 12px 20px; margin-top: 20px;
                font-size: 16px; color: white; background-color: #007bff;
                border-radius: 5px; text-decoration: none;">
                ▶️ Listen or Download Audio
              </a>
            </p>
            <p style="margin-top: 40px; font-size: 14px; color: #666;">
              Thank you for using <strong>Text-to-Audio</strong>!<br/>
              This link will expire in 1 hour.
            </p>
          </div>
        </body>
        </html>
        """

        print(f"Sending email to {recipient} with audio link: {audio_url}")
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [recipient]},
            Message={
                'Subject': {'Data': '🎧 Your Audio is Ready!'},
                'Body': {
                    'Html': {'Data': html_content},
                    'Text': {'Data': f"Your audio is ready: {audio_url}"}
                }
            }
        )
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:")
        print(str(e))


def lambda_handler(event, context):
    print(event)
    for record in event['Records']:
        key = unquote_plus(record['s3']['object']['key'])
        bucket = record['s3']['bucket']['name']

        if not (key.endswith('.pdf') or key.endswith('.docx')):
            continue

        try:
            file_id, voice, email = key.split("/")[-1].replace(".pdf", "").replace(".docx", "").split("___")
        except:
            voice = "Joanna"
            email = None
            file_id = str(uuid.uuid4())

        text = extract_text(bucket, key)
        if not text:
            continue

        text = text[:3000]
        response = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId=voice)

        audio_key = f"audio/{file_id}.mp3"
        s3.upload_fileobj(response['AudioStream'], bucket, audio_key)

        if email:
            audio_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': audio_key},
                ExpiresIn=3600
            )
            send_email(email, audio_url)

    return {'statusCode': 200, 'body': 'Audio created'}
