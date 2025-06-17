# 📄 Text-to-Audio Convertor Web App using AWS (PDF to MP3 + Email Delivery)

This project is a **real-world, serverless web application** built on AWS that allows users to:

* Upload a **PDF or DOCX** file
* Select a **Polly voice**
* Convert the document's text into **MP3 audio**
* Automatically **email the generated audio file** to the user


---

## 🧰 Tech Stack

| Layer      | Technology            |
| ---------- | --------------------- |
| Frontend   | HTML, CSS, JavaScript |
| Backend    | AWS Lambda (Python)   |
| Storage    | Amazon S3             |
| TTS Engine | Amazon Polly          |
| Email      | Amazon SES            |
| API        | Amazon API Gateway    |

---

## 🧐 How It Works

1. **User uploads a document** via the web interface and selects a voice + email.
2. **Frontend calls an API Gateway endpoint**, which invokes a Lambda function to generate a **presigned S3 upload URL**.
3. The document is **uploaded to S3** using the presigned URL.
4. S3 triggers another Lambda function (`convertTextToAudio`) when a file is uploaded to `uploads/`.
5. This function:

   * Extracts text from the file (using PyPDF2 for PDF or docx2txt for DOCX)
   * Sends the text to **Amazon Polly** to generate audio
   * Uploads the MP3 to `audio/` in S3
   * Generates a presigned download link for the audio
   * Sends an email via **Amazon SES** with the link

---

## 💪 Features

* ✅ PDF and DOCX file support
* ✅ Upload via secure, presigned S3 URLs
* ✅ Choose from multiple Amazon Polly voices
* ✅ Email delivery with clickable download/play link
* ✅ No servers to manage (fully serverless)

---

## 🌍 Architecture Diagram

```
[Frontend] --(POST)--> [API Gateway] --> [Lambda: generateUploadUrl] --> [S3: uploads/]
                                                                 |
                                                                 V
                                                           [Presigned URL]

[S3: uploads/] --(Trigger)--> [Lambda: convertTextToAudio] --> [Amazon Polly]
                                                                  |
                                                                  V
                                                       [S3: audio/] --> [SES Email to User]
```

---

## 🔐 Security

* ✅ S3 Bucket is private with **Block All Public Access** enabled
* ✅ All access is granted via **temporary presigned URLs**
* ✅ IAM policies restrict each Lambda to only necessary actions

---

## 📆 Project Structure

```
text-to-audio-project/
├── frontend/
│   └── index.html
├── lambdas/
│   ├── generateUploadUrl.py
│   └── convertTextToAudio.py
├── assets/
│   ├── architecture.drawio
│   └── thumbnail.png
└── README.md
```

---

## 🧲 Environment Variables

These should be set in the Lambda configuration:

| Variable       | Description                              |
| -------------- | ---------------------------------------- |
| `BUCKET_NAME`  | Name of your S3 bucket                   |
| `SENDER_EMAIL` | Verified SES email to send messages from |

---

## 📨 Sample Email Output

* Subject: `Your Audio is Ready!`
* Body: Styled HTML message with download/play button
* Link is valid for 1 hour (presigned URL)

---

## 🚀 Deployment Notes

* Deploy Lambda functions via AWS Console or SAM/CDK
* Configure S3 bucket with appropriate **CORS** and **Event triggers**
* Verify sender & recipient emails in **Amazon SES** (if in sandbox mode)

---

## 🥻 Author

**Alfonce Morara**
📧 [alfoncemorara412@gmail.com](mailto:alfoncemorara412@gmail.com)

---

