from rest_framework import serializers

from .models import Booking
from diagnostics.models import DiagnosticCentre, DiagnosticTest


class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking

        fields = [
            "id",
            "centre",
            "test",
            "appointment_datetime",
            "status",
            "amount",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "amount",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):

        centre = attrs["centre"]
        test = attrs["test"]

        if not centre.is_active:
            raise serializers.ValidationError(
                {
                    "centre": "This diagnostic centre is not active."
                }
            )

        if not test.is_active:
            raise serializers.ValidationError(
                {
                    "test": "This diagnostic test is not active."
                }
            )

        if test.centre_id != centre.id:
            raise serializers.ValidationError(
                {
                    "test": "This test does not belong to the selected diagnostic centre."
                }
            )

        return attrs

    def create(self, validated_data):

        test = validated_data["test"]

        validated_data["amount"] = test.price

        validated_data["user"] = self.context["request"].user

        return Booking.objects.create(**validated_data)