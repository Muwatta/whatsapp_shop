import requests
from decouple import config
from urllib.parse import urljoin

WHATSAPP_TOKEN = config("WHATSAPP_TOKEN")
PHONE_ID = config("WHATSAPP_PHONE_ID")
API_BASE = config("WHATSAPP_API_BASE", default="https://graph.facebook.com/v19.0")
MESSAGES_URL = f"{API_BASE}/{PHONE_ID}/messages"
MEDIA_URL = f"{API_BASE}/{PHONE_ID}/media"

HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_TOKEN}",
}

def send_text(phone_number, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    res = requests.post(MESSAGES_URL, headers={**HEADERS, "Content-Type":"application/json"}, json=payload)
    return res.json()

def upload_media(file_path, mime_type="application/pdf"):
    # Upload file (multipart/form-data) to WhatsApp Cloud API and get media id
    files = {
        'file': (file_path.split("/")[-1], open(file_path, 'rb'), mime_type)
    }
    data = {}
    res = requests.post(MEDIA_URL, headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"}, files=files, data=data)
    return res.json()

def send_document(phone_number, media_id, filename="receipt.pdf"):
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": filename
        }
    }
    res = requests.post(MESSAGES_URL, headers={**HEADERS, "Content-Type":"application/json"}, json=payload)
    return res.json()
