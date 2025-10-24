import json, uuid
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from .models import Product, Customer, Order
from .payments import initialize_payment, verify_payment
from .utils import generate_receipt_pdf
from .whatsapp_api import send_text, upload_media, send_document
from django.shortcuts import get_object_or_404

VERIFY_TOKEN = config("VERIFY_TOKEN")
BASE_URL = config("BASE_URL", default="http://localhost:8000")

@csrf_exempt
def webhook(request):
    if request.method == "GET":
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse("Invalid token", status=403)

    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
        # Basic parsing — adapt per actual WhatsApp webhook structure
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    from_phone = msg.get("from")  # WhatsApp number
                    text = msg.get("text", {}).get("body") or ""
                    # For QR-scanned product we expect "ProductName|Price" (as we encoded)
                    if "|" in text:
                        # QR scanned flow: e.g., "Bread|200"
                        try:
                            name, price = text.split("|")
                            product = Product.objects.filter(name__iexact=name.strip()).first()
                            if not product:
                                # create product if not exists (optional)
                                product = Product.objects.create(name=name.strip(), price=float(price))
                            # find or create customer
                            cust, _ = Customer.objects.get_or_create(phone=from_phone, defaults={"name": from_phone})
                            # create an order with qty 1 default
                            order = Order.objects.create(customer=cust, product=product, quantity=1, total_amount=product.price)
                            # initialize payment
                            reference = str(uuid.uuid4())
                            # For email required by paystack, use placeholder or ask user — here we use phone@local.fake
                            init = initialize_payment(email=f"{from_phone}@example.com", amount=float(order.total_amount), reference=reference)
                            checkout_url = init.get("data", {}).get("authorization_url")
                            # Save reference somewhere — simplest: save to order (if you extended model) or use cache. For now we attach to order via attribute
                            order.reference = reference
                            order.save()
                            # message user with payment link
                            send_text(from_phone, f"Order #{order.id} for {product.name} (₦{product.price}). Pay here: {checkout_url}")
                        except Exception as e:
                            send_text(from_phone, f"Sorry, I couldn't process that QR: {str(e)}")
                    else:
                        # If user sends plain "buy <product>" or "order bread 2" simple parsing:
                        words = text.lower().split()
                        if "order" in words or "buy" in words:
                            # naive parsing: find product in DB
                            for p in Product.objects.all():
                                if p.name.lower() in text.lower():
                                    qty = 1
                                    # try to find quantity
                                    for w in words:
                                        if w.isdigit():
                                            qty = int(w)
                                    cust, _ = Customer.objects.get_or_create(phone=from_phone, defaults={"name": from_phone})
                                    order = Order.objects.create(customer=cust, product=p, quantity=qty, total_amount=p.price*qty)
                                    reference = str(uuid.uuid4())
                                    init = initialize_payment(email=f"{from_phone}@example.com", amount=float(order.total_amount), reference=reference)
                                    checkout_url = init.get("data", {}).get("authorization_url")
                                    order.reference = reference
                                    order.save()
                                    send_text(from_phone, f"Order #{order.id} for {p.name} (x{qty}) created. Pay here: {checkout_url}")
                                    break
                        else:
                            # default reply
                            send_text(from_phone, "Hello! Scan product QR or send 'order <product>' to place an order.")
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "ignored"})
def get_products(request):
    products = Product.objects.all()
    data = [{"id": p.id, "name": p.name, "price": float(p.price)} for p in products]
    return JsonResponse({"products": data})