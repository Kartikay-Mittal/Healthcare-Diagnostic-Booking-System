from django.urls import path

from .views import (
    PaymentListCreateView,
    PaymentProcessView,
    PaymentWebhookView,
)

urlpatterns = [
    path(
        "payments/",
        PaymentListCreateView.as_view(),
        name="payment-list-create",
    ),

    path(
        "payments/<int:pk>/process/",
        PaymentProcessView.as_view(),
        name="payment-process",
    ),

    path(
        "payments/webhook/",
        PaymentWebhookView.as_view(),
        name="payment-webhook",
    ),
]