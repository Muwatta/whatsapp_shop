import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import Order
from .payments import verify_payment
from .utils import generate_receipt_pdf
from .whatsapp_api import upload_media, send_document, send_text

@csrf_exempt
def paystack_webhook(request):
    # For Paystack, you should verify signature header; omitted for brevity — add in production!
    if request.method != "POST":
        return HttpResponse(status=405)
    payload = json.loads(request.body.decode("utf-8"))
    event = payload.get("event")
    data = payload.get("data", {})
    if event == "charge.success" or data.get("status") == "success":
        reference = data.get("reference")
        # find order by reference
        try:
            order = Order.objects.get(reference=reference)
        except Order.DoesNotExist:
            return JsonResponse({"ok": False, "reason": "order not found"}, status=404)

        # verify with Paystack for safety
        res = verify_payment(reference)
        if res.get("data", {}).get("status") == "success":
            order.is_paid = True
            order.save()
            # create receipt
            pdf_path = generate_receipt_pdf(order)
            upload_resp = upload_media(pdf_path)
            media_id = upload_resp.get("id")
            if media_id:
                send_document(order.customer.phone, media_id, filename=f"receipt_order_{order.id}.pdf")
            else:
                send_text(order.customer.phone, "Payment received but I couldn't attach receipt. We'll send it soon.")
            return JsonResponse({"received": True})
    return JsonResponse({"ok": True})
