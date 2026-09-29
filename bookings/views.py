from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )


class BookingCancelView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        )

    def patch(self, request, *args, **kwargs):
        booking = self.get_object()

        if booking.status != Booking.Status.PENDING:
            return Response(
                {
                    "detail": "Only pending bookings can be cancelled."
                },
                status=400,
            )

        booking.status = Booking.Status.CANCELLED

        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        serializer = self.get_serializer(booking)

        return Response(serializer.data)