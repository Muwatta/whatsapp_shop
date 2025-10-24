from django.urls import path
from . import views
from .payment_webhook import paystack_webhook

urlpatterns = [
    path("webhook/", views.webhook, name="webhook"),                 # WhatsApp webhook
    path("payment/webhook/", paystack_webhook, name="paystack_webhook"),  # Paystack webhook
    path("products/", views.get_products, name="get_products"),
]
