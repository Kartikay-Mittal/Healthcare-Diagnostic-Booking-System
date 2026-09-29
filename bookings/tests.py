from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from diagnostics.models import DiagnosticCentre, DiagnosticTest
from .models import Booking


User = get_user_model()


class BookingTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="bookingtest@example.com",
            username="bookingtest",
            password="TestPassword123",
        )

        self.other_user = User.objects.create_user(
            email="otherbooking@example.com",
            username="otherbooking",
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

        self.other_centre = DiagnosticCentre.objects.create(
            name="Other Diagnostic Centre",
            address="Other Address",
            city="Delhi",
            state="Delhi",
            phone="+918888888888",
        )

        self.other_test = DiagnosticTest.objects.create(
            centre=self.other_centre,
            name="Other Blood Test",
            description="Other diagnostic test",
            price=799.00,
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_create_booking(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.test.id,
                "appointment_datetime": "2026-10-20T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        booking = Booking.objects.get(id=response.data["id"])

        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.centre, self.centre)
        self.assertEqual(booking.test, self.test)
        self.assertEqual(
            booking.appointment_datetime,
            timezone.make_aware(
                 datetime(2026, 10, 20, 10, 30),
                 timezone=timezone.get_fixed_timezone(330),
            ),
        )
        self.assertEqual(booking.status, Booking.Status.PENDING)
        self.assertEqual(float(booking.amount), 499.00)

    def test_booking_amount_is_taken_from_test_price(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.test.id,
                "appointment_datetime": "2026-10-20T10:30:00+05:30",
                "amount": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        booking = Booking.objects.get(id=response.data["id"])

        self.assertEqual(float(booking.amount), 499.00)

    def test_booking_rejects_test_from_different_centre(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.other_test.id,
                "appointment_datetime": "2026-10-21T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("test", response.data)

    def test_booking_rejects_inactive_centre(self):
        self.centre.is_active = False
        self.centre.save()

        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.test.id,
                "appointment_datetime": "2026-10-22T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("centre", response.data)

    def test_booking_rejects_inactive_test(self):
        self.test.is_active = False
        self.test.save()

        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.test.id,
                "appointment_datetime": "2026-10-23T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("test", response.data)

    def test_pending_booking_can_be_cancelled(self):
        booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 25, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.PENDING,
        )

        response = self.client.patch(
            f"/api/bookings/{booking.id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        booking.refresh_from_db()

        self.assertEqual(booking.status, Booking.Status.CANCELLED)

    def test_confirmed_booking_cannot_be_cancelled(self):
        booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 26, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.CONFIRMED,
        )

        response = self.client.patch(
            f"/api/bookings/{booking.id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_failed_booking_cannot_be_cancelled(self):
        booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 27, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.FAILED,
        )

        response = self.client.patch(
            f"/api/bookings/{booking.id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_user_cannot_access_another_users_booking(self):
        booking = Booking.objects.create(
            user=self.other_user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 28, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.PENDING,
        )

        response = self.client.get(
            f"/api/bookings/{booking.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_only_see_own_bookings(self):
        Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 29, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.PENDING,
        )

        Booking.objects.create(
            user=self.other_user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 10, 30, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.PENDING,
        )

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_unauthenticated_user_cannot_create_booking(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.test.id,
                "appointment_datetime": "2026-10-31T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_list_bookings(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/bookings/")

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_view_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 11, 1, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.PENDING,
        )

        self.client.force_authenticate(user=None)

        response = self.client.get(
            f"/api/bookings/{booking.id}/"
        )

        self.assertEqual(response.status_code, 401)

    def test_unauthenticated_user_cannot_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 11, 2, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.PENDING,
        )

        self.client.force_authenticate(user=None)

        response = self.client.patch(
            f"/api/bookings/{booking.id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_cancelled_booking_cannot_be_cancelled_again(self):
        booking = Booking.objects.create(
            user=self.user,
            centre=self.centre,
            test=self.test,
            appointment_datetime=timezone.make_aware(
                datetime(2026, 11, 3, 10, 30)
            ),
            amount=self.test.price,
            status=Booking.Status.CANCELLED,
        )

        response = self.client.patch(
            f"/api/bookings/{booking.id}/cancel/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)

    def test_booking_rejects_invalid_centre(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": 99999,
                "test": self.test.id,
                "appointment_datetime": "2026-11-04T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("centre", response.data)

    def test_booking_rejects_invalid_test(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": 99999,
                "appointment_datetime": "2026-11-05T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("test", response.data)

    def test_booking_rejects_missing_centre(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "test": self.test.id,
                "appointment_datetime": "2026-11-06T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("centre", response.data)

    def test_booking_rejects_missing_test(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "appointment_datetime": "2026-11-07T10:30:00+05:30",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("test", response.data)

    def test_booking_rejects_missing_appointment_datetime(self):
        response = self.client.post(
            "/api/bookings/",
            {
                "centre": self.centre.id,
                "test": self.test.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("appointment_datetime", response.data)
