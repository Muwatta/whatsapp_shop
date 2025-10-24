import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings

def generate_receipt_pdf(order, filename=None):
    if filename is None:
        filename = f"receipt_order_{order.id}.pdf"
    out_path = os.path.join(settings.MEDIA_ROOT, "receipts")
    os.makedirs(out_path, exist_ok=True)
    filepath = os.path.join(out_path, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, 800, "Payment Receipt")
    c.setFont("Helvetica", 12)
    c.drawString(60, 770, f"Order ID: {order.id}")
    c.drawString(60, 750, f"Customer: {order.customer.name} ({order.customer.phone})")
    c.drawString(60, 730, f"Product: {order.product.name}")
    c.drawString(60, 710, f"Quantity: {order.quantity}")
    c.drawString(60, 690, f"Amount: ₦{order.total_amount}")
    c.drawString(60, 670, f"Status: {'PAID' if order.is_paid else 'UNPAID'}")
    c.drawString(60, 640, "Thank you for your purchase!")
    c.showPage()
    c.save()
    return filepath
