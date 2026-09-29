from rest_framework import serializers

from .models import Payment
from bookings.models import Booking


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment

        fields = [
            "id",
            "booking",
            "amount",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "amount",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]

    def validate_booking(self, booking):

        request = self.context["request"]

        if booking.user != request.user:
            raise serializers.ValidationError(
                "You can only make payments for your own bookings."
            )

        if booking.status == Booking.Status.CANCELLED:
            raise serializers.ValidationError(
                "Cannot make payment for a cancelled booking."
            )

        return booking

    def create(self, validated_data):

        booking = validated_data["booking"]

        validated_data["amount"] = booking.amount

        return Payment.objects.create(
            **validated_data
        )

class PaymentWebhookSerializer(serializers.Serializer):

    event_id = serializers.CharField(
        max_length=100
    )

    transaction_id = serializers.CharField(
        max_length=100
    )

    status = serializers.ChoiceField(
        choices=[
            Payment.Status.SUCCESS,
            Payment.Status.FAILED,
        ]
    )