import qrcode
from PIL import Image
from django.conf import settings
import os

def generate_qr(product_name, price):
    data = f"{product_name}|{price}"
    qr = qrcode.make(data)
    path = os.path.join(settings.BASE_DIR, "static/qr", f"{product_name}.png")
    qr.save(path)
    return path
