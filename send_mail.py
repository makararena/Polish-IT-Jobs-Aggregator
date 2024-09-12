import os
import smtplib
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

def send_email(subject, body, to_email, attachment_path=None):
    print(f"\n{'-' * 40}")
    print(f"Seding email to {to_email}")
    print(f"\n{'-' * 40}")
    from_email = 'makararena.pl@gmail.com'
    password = os.getenv("EMAIL_PASSWORD")

    if password is None:
        raise ValueError("EMAIL_PASSWORD environment variable not set")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        try:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                filename = os.path.basename(attachment_path)
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(part)
        except FileNotFoundError:
            print(f"Attachment file {attachment_path} not found")
            return

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send an email with optional attachment.')
    parser.add_argument('--subject', required=True, help='Subject of the email')
    parser.add_argument('--body', required=True, help='Body of the email')
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--attachment', help='Path to the attachment file')

    args = parser.parse_args()

    send_email(args.subject, args.body, args.to, args.attachment)