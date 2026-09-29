from datetime import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from bookings.models import Booking
from diagnostics.models import DiagnosticCentre, DiagnosticTest
from payments.models import Payment

from rest_framework.test import APIClient


User = get_user_model()


class PaymentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="paymenttest@example.com",
            username="paymenttest",
            password="TestPassword123",
        )

        self.centre = DiagnosticCentre.objects.create(
            name="Test Diagnostic Centre",
            address="Test Address",
            city="Noida",
            state="Uttar Pradesh",
            phone="+919999999999",
        )

        self.test = DiagnosticTest.objects.create(
            centre=self.centre,
            name="Test Blood Test",
            description="Test diagnostic test",
            price=499.00,
        )

        self.booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 20, 10, 30)
            ),
            amount=self.test.price,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_payment_amount_is_taken_from_booking(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
        )

        self.assertEqual(
            payment.amount,
            self.booking.amount,
        )

    def test_payment_amount_cannot_be_changed_by_client(self):
        with patch(
            "payments.views.random.choice",
            return_value=Payment.Status.SUCCESS,
        ):
            response = self.client.post(
                "/api/payments/",
                {
                    "booking": self.booking.id,
                    "amount": 1.00,
                },
                format="json",
            )

        self.assertEqual(response.status_code, 201)

        payment = Payment.objects.get(
            id=response.data["payment"]["id"]
        )

        self.assertEqual(
            payment.amount,
            self.booking.amount,
        )

    def test_user_cannot_pay_for_another_users_booking(self):
        other_user = User.objects.create_user(
            email="otheruser@example.com",
            username="otheruser",
            password="TestPassword123",
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "You can only make payments for your own bookings.",
            str(response.data),
        )

    def test_cancelled_booking_cannot_be_paid(self):
        self.booking.status = Booking.Status.CANCELLED
        self.booking.save()

        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "Cannot make payment for a cancelled booking.",
            str(response.data),
        )

    @patch(
        "payments.views.random.choice",
        return_value=Payment.Status.SUCCESS,
    )
    def test_payment_endpoint_simulates_success(
        self,
        mock_choice,
    ):
        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        payment = Payment.objects.get(
            id=response.data["payment"]["id"]
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status,
            Payment.Status.SUCCESS,
        )

        self.assertIsNotNone(
            payment.transaction_id
        )

        self.assertTrue(
            payment.transaction_id.startswith("SIM-")
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

    @patch(
        "payments.views.random.choice",
        return_value=Payment.Status.FAILED,
    )
    def test_payment_endpoint_simulates_failure(
        self,
        mock_choice,
    ):
        response = self.client.post(
            "/api/payments/",
            {
                "booking": self.booking.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        payment = Payment.objects.get(
            id=response.data["payment"]["id"]
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status,
            Payment.Status.FAILED,
        )

        self.assertIsNotNone(
            payment.transaction_id
        )

        self.assertTrue(
            payment.transaction_id.startswith("SIM-")
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.FAILED,
        )

    @patch(
        "payments.views.random.choice",
        return_value=Payment.Status.SUCCESS,
    )
    def test_process_payment_generates_transaction_and_confirms_booking(
        self,
        mock_choice,
    ):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
        )

        response = self.client.post(
            f"/api/payments/{payment.id}/process/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertIsNotNone(
            payment.transaction_id
        )

        self.assertTrue(
            payment.transaction_id.startswith("SIM-")
        )

        self.assertEqual(
            payment.status,
            Payment.Status.SUCCESS,
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

    def test_success_webhook_confirms_payment_and_booking(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
            transaction_id="SIM-SUCCESS123",
        )

        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_test_success",
                "transaction_id": payment.transaction_id,
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status,
            Payment.Status.SUCCESS,
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

        self.assertEqual(
            payment.webhook_event_id,
            "evt_test_success",
        )

    def test_failed_webhook_fails_payment_and_booking(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
            transaction_id="SIM-FAILED123",
        )

        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_test_failed",
                "transaction_id": payment.transaction_id,
                "status": "FAILED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status,
            Payment.Status.FAILED,
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.FAILED,
        )

        self.assertEqual(
            payment.webhook_event_id,
            "evt_test_failed",
        )

    def test_duplicate_webhook_is_idempotent(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
            transaction_id="SIM-DUPLICATE123",
        )

        webhook_data = {
            "event_id": "evt_test_duplicate",
            "transaction_id": payment.transaction_id,
            "status": "SUCCESS",
        }

        first_response = self.client.post(
            "/api/payments/webhook/",
            webhook_data,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status,
            Payment.Status.SUCCESS,
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

        second_response = self.client.post(
            "/api/payments/webhook/",
            webhook_data,
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            200,
        )

        self.assertEqual(
            second_response.data["message"],
            "Webhook already processed.",
        )

        self.assertEqual(
            Payment.objects.count(),
            1,
        )

    def test_webhook_with_unknown_transaction_id_returns_404(self):
        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_unknown",
                "transaction_id": "SIM-DOESNOTEXIST",
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.data["detail"],
            "Payment not found.",
        )

    def test_webhook_rejects_invalid_status(self):
        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_invalid_status",
                "transaction_id": "SIM-INVALID123",
                "status": "COMPLETED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "status",
            response.data,
        )

    def test_webhook_rejects_missing_required_fields(self):
        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_missing_fields",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertIn(
            "transaction_id",
            response.data,
        )

        self.assertIn(
            "status",
            response.data,
        )



    def test_finalized_payment_cannot_be_reversed_by_webhook(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
            status=Payment.Status.SUCCESS,
            transaction_id="SIM-FINAL123",
        )

        self.booking.status = Booking.Status.CONFIRMED
        self.booking.save()

        response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_reverse_attempt",
                "transaction_id": payment.transaction_id,
                "status": "FAILED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        payment.refresh_from_db()
        self.booking.refresh_from_db()

        self.assertEqual(
            payment.status,
            Payment.Status.SUCCESS,
        )

        self.assertEqual(
            self.booking.status,
            Booking.Status.CONFIRMED,
        )

    def test_webhook_event_id_cannot_be_reused_for_another_payment(self):
        first_payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
            transaction_id="SIM-FIRST123",
        )

        first_response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_shared",
                "transaction_id": first_payment.transaction_id,
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        second_booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 21, 10, 30)
            ),
            amount=self.test.price,
        )

        second_payment = Payment.objects.create(
            booking=second_booking,
            amount=second_booking.amount,
            transaction_id="SIM-SECOND123",
        )

        second_response = self.client.post(
            "/api/payments/webhook/",
            {
                "event_id": "evt_shared",
                "transaction_id": second_payment.transaction_id,
                "status": "SUCCESS",
            },
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )