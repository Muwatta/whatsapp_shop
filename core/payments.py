import requests
from decouple import config
PAYSTACK_SECRET = config("PAYSTACK_SECRET_KEY")
CALLBACK = config("PAYMENT_CALLBACK_URL")

def initialize_payment(email, amount, reference):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    data = {"email": email, "amount": int(amount * 100), "reference": reference, "callback_url": CALLBACK}
    r = requests.post(url, headers=headers, json=data)
    return r.json()

def verify_payment(reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    r = requests.get(url, headers=headers)
    return r.json()
