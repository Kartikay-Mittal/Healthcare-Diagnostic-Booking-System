from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import DiagnosticCentre, DiagnosticTest
from .serializers import DiagnosticCentreSerializer, DiagnosticTestSerializer


class DiagnosticCentreListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        return DiagnosticCentre.objects.filter(is_active=True)


class DiagnosticCentreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiagnosticCentre.objects.all()
    serializer_class = DiagnosticCentreSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        return DiagnosticCentre.objects.filter(is_active=True)


class DiagnosticTestListCreateView(generics.ListCreateAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        return DiagnosticTest.objects.filter(is_active=True)


class DiagnosticTestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DiagnosticTest.objects.all()
    serializer_class = DiagnosticTestSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        return DiagnosticTest.objects.all()