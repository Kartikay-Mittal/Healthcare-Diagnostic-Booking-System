import random
import uuid

from django.db import transaction

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking

from .models import Payment
from .serializers import PaymentSerializer, PaymentWebhookSerializer


class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        ).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            payment = serializer.save()

            payment.transaction_id = (
                f"SIM-{uuid.uuid4().hex[:12].upper()}"
            )

            payment.status = random.choice(
                [
                    Payment.Status.SUCCESS,
                    Payment.Status.FAILED,
                ]
            )

            payment.save(
                update_fields=[
                    "transaction_id",
                    "status",
                    "updated_at",
                ]
            )

            booking = payment.booking

            if payment.status == Payment.Status.SUCCESS:
                booking.status = Booking.Status.CONFIRMED
            else:
                booking.status = Booking.Status.FAILED

            booking.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        response_serializer = self.get_serializer(payment)

        return Response(
            {
                "message": "Payment simulated successfully.",
                "payment": response_serializer.data,
                "booking_status": booking.status,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentProcessView(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            booking__user=self.request.user
        )

    def post(self, request, *args, **kwargs):
        payment = self.get_object()

        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    "detail": "Only pending payments can be processed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            payment.transaction_id = (
                f"SIM-{uuid.uuid4().hex[:12].upper()}"
            )

            payment.status = random.choice(
                [
                    Payment.Status.SUCCESS,
                    Payment.Status.FAILED,
                ]
            )

            payment.save(
                update_fields=[
                    "transaction_id",
                    "status",
                    "updated_at",
                ]
            )

            booking = payment.booking

            if payment.status == Payment.Status.SUCCESS:
                booking.status = Booking.Status.CONFIRMED
            else:
                booking.status = Booking.Status.FAILED

            booking.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        serializer = self.get_serializer(payment)

        return Response(
            {
                "message": "Payment simulated successfully.",
                "payment": serializer.data,
                "booking_status": booking.status,
            },
            status=status.HTTP_200_OK,
        )


class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PaymentWebhookSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        event_id = serializer.validated_data["event_id"]
        transaction_id = serializer.validated_data["transaction_id"]
        webhook_status = serializer.validated_data["status"]

        with transaction.atomic():
            payment = (
                Payment.objects
                .select_for_update()
                .filter(transaction_id=transaction_id)
                .first()
            )

            if payment is None:
                return Response(
                    {"detail": "Payment not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Same event for the same payment = idempotent request
            if payment.webhook_event_id == event_id:
                return Response(
                    {"message": "Webhook already processed."},
                    status=status.HTTP_200_OK,
                )

            # A finalized payment cannot be changed by another webhook
            if payment.status in [
                Payment.Status.SUCCESS,
                Payment.Status.FAILED,
            ]:
                return Response(
                    {
                        "detail": (
                            "Payment has already been finalized "
                            "and cannot be changed."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # An event ID can only belong to one payment
            existing_event = (
                Payment.objects
                .select_for_update()
                .filter(webhook_event_id=event_id)
                .exclude(id=payment.id)
                .first()
            )

            if existing_event is not None:
                return Response(
                    {
                        "detail": (
                            "This webhook event has already been processed."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment.webhook_event_id = event_id
            payment.status = webhook_status

            payment.save(
                update_fields=[
                    "webhook_event_id",
                    "status",
                    "updated_at",
                ]
            )

            booking = payment.booking

            if webhook_status == Payment.Status.SUCCESS:
                booking.status = Booking.Status.CONFIRMED

            elif webhook_status == Payment.Status.FAILED:
                booking.status = Booking.Status.FAILED

            booking.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            {
                "message": "Webhook processed successfully.",
                "payment_id": payment.id,
                "booking_id": booking.id,
                "payment_status": payment.status,
                "booking_status": booking.status,
            },
            status=status.HTTP_200_OK,
        )