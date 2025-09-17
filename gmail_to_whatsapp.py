"""
Program: Gmail to WhatsApp Forwarder
Author: Muubii Bytes
Description:
    - Connects to Gmail via Gmail API
    - Fetches specific emails (based on filters you choose)
    - Forwards the email text to WhatsApp via WhatsApp Cloud API
"""
import base64
import os.path
import requests
from dotenv import load_dotenv   # 👈 load .env

# Load environment variables from .env
load_dotenv()

# Google API client imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ------------------- CONFIGURATION -------------------

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
TO_PHONE_NUMBER = os.getenv("TO_PHONE_NUMBER")
print("WhatsApp Token (first 10 chars):", str(WHATSAPP_TOKEN)[:10])  # debug

# ------------------- AUTHENTICATION -------------------

def gmail_authenticate():
    """
    Authenticate and build Gmail API service
    Always request a refresh_token if missing
    """
    creds = None

    # Load existing token if available
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid creds, login again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 👇 Force refresh_token by setting prompt='consent' + access_type='offline'
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(
                port=8080,
                prompt="consent"   # <--- important!
            )

        # Save token (with refresh_token inside)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)



# ------------------- FETCH EMAILS -------------------

def fetch_emails(service, query="from:scholarship@example.com is:unread"):
    """
    Fetch unread emails that match the given query
    Example queries:
      - "is:unread"
      - "from:someone@example.com"
      - "subject:Scholarship"
    """
    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])

    emails = []
    if not messages:
        print("No matching emails found.")
        return emails

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        payload = msg_data["payload"]
        headers = payload["headers"]

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        # Extract body (plain text or HTML fallback)
        body = ""
        if "data" in payload["body"]:
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        else:
            parts = payload.get("parts", [])
            for part in parts:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break

        emails.append({
            "subject": subject,
            "from": sender,
            "body": body
        })

    return emails


# ------------------- FORWARD TO WHATSAPP -------------------

def send_whatsapp_message(message_text):
    """
    Send a WhatsApp message using Meta WhatsApp Cloud API
    """
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": TO_PHONE_NUMBER,
        "type": "text",
        "text": {"body": message_text}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ Message sent to WhatsApp successfully.")
    else:
        print("❌ Failed to send message:", response.text)


# ------------------- MAIN SCRIPT -------------------

if __name__ == "__main__":
    service = gmail_authenticate()

    # Choose your filter (modify as needed)
    emails = fetch_emails(service, query="subject:Scholarship is:unread")

    for email in emails:
        text_message = f"📩 New Email\nFrom: {email['from']}\nSubject: {email['subject']}\n\n{email['body']}"
        send_whatsapp_message(text_message)
