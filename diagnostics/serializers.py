from rest_framework import serializers

from .models import DiagnosticCentre, DiagnosticTest


class DiagnosticTestSerializer(serializers.ModelSerializer):
    centre = serializers.PrimaryKeyRelatedField(
        queryset=DiagnosticCentre.objects.filter(is_active=True),
        write_only=True,
    )

    class Meta:
        model = DiagnosticTest
        fields = [
            "id",
            "centre",
            "name",
            "description",
            "price",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class DiagnosticCentreSerializer(serializers.ModelSerializer):
    tests = DiagnosticTestSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = DiagnosticCentre
        fields = [
            "id",
            "name",
            "address",
            "city",
            "state",
            "phone",
            "is_active",
            "created_at",
            "tests",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "tests",
        ]