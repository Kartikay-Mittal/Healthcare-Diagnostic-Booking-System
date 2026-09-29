from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from .models import DiagnosticCentre, DiagnosticTest

User = get_user_model()

class DiagnosticTests(TestCase):


    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@example.com",
            username="testuser",
            password="TestPassword123",
        )

        self.admin = User.objects.create_user(
            email="admin@example.com",
            username="adminuser",
            password="AdminPass123",
            is_staff=True,
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

    def test_unauthenticated_user_cannot_list_centres(self):
        response = self.client.get(
            "/api/centres/"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_authenticated_user_can_list_centres(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/centres/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.centre.id,
        )

    def test_centre_contains_nested_tests(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            f"/api/centres/{self.centre.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "tests",
            response.data,
        )

        self.assertEqual(
            len(response.data["tests"]),
            1,
        )

        self.assertEqual(
            response.data["tests"][0]["id"],
            self.test.id,
        )

        self.assertEqual(
            response.data["tests"][0]["name"],
            "Test Blood Test",
        )

        self.assertEqual(
            float(response.data["tests"][0]["price"]),
            499.00,
        )

    def test_authenticated_user_can_view_centre_detail(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            f"/api/centres/{self.centre.id}/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["id"],
            self.centre.id,
        )

        self.assertEqual(
            response.data["name"],
            "Test Diagnostic Centre",
        )

    def test_nonexistent_centre_returns_404(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/api/centres/99999/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_inactive_centre_is_not_listed(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.centre.is_active = False
        self.centre.save()

        response = self.client.get(
            "/api/centres/"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_inactive_centre_returns_404_for_detail(self):
        self.client.force_authenticate(
            user=self.user
        )

        self.centre.is_active = False
        self.centre.save()

        response = self.client.get(
            f"/api/centres/{self.centre.id}/"
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_centre_returns_correct_information(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            f"/api/centres/{self.centre.id}/"
        )

        self.assertEqual(
            response.data["name"],
            "Test Diagnostic Centre",
        )

        self.assertEqual(
            response.data["address"],
            "Test Address",
        )

        self.assertEqual(
            response.data["city"],
            "Noida",
        )

        self.assertEqual(
            response.data["state"],
            "Uttar Pradesh",
        )

        self.assertEqual(
            response.data["phone"],
            "+919999999999",
        )

        self.assertTrue(
            response.data["is_active"]
        )

    def test_normal_user_cannot_create_centre(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/centres/",
            {
                "name": "New Diagnostic Centre",
                "address": "Test Address",
                "city": "Noida",
                "state": "Uttar Pradesh",
                "phone": "+91 9999999999",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )



    def test_admin_can_create_centre(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            "/api/centres/",
            {
                "name": "Admin Diagnostic Centre",
                "address": "Admin Test Address",
                "city": "Delhi",
                "state": "Delhi",
                "phone": "+91 8888888888",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["name"],
            "Admin Diagnostic Centre",
        )

        self.assertEqual(
            DiagnosticCentre.objects.count(),
            2,
        )
    
            
    def test_normal_user_cannot_update_centre(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        response = self.client.patch(
            f"/api/centres/{self.centre.id}/",
            {
                "name": "Modified Centre",
            },
            format="json",
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    
    def test_normal_user_cannot_delete_centre(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        response = self.client.delete(
            f"/api/centres/{self.centre.id}/"
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    
    def test_admin_can_update_centre(self):
        self.client.force_authenticate(
            user=self.admin
        )
    
        response = self.client.patch(
            f"/api/centres/{self.centre.id}/",
            {
                "name": "Updated Diagnostic Centre",
            },
            format="json",
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
    
        self.assertEqual(
            response.data["name"],
            "Updated Diagnostic Centre",
        )
    
    def test_admin_can_delete_centre(self):
        self.client.force_authenticate(
            user=self.admin
        )
    
        response = self.client.delete(
            f"/api/centres/{self.centre.id}/"
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
    
        self.assertFalse(
            DiagnosticCentre.objects.filter(
                id=self.centre.id
            ).exists()
        )
    
    def test_normal_user_cannot_create_test(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        response = self.client.post(
            "/api/tests/",
            {
                "centre": self.centre.id,
                "name": "New Blood Test",
                "description": "New test",
                "price": "599.00",
            },
            format="json",
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    
    def test_admin_can_create_test(self):
        self.client.force_authenticate(
            user=self.admin
        )
    
        response = self.client.post(
            "/api/tests/",
            {
                "centre": self.centre.id,
                "name": "Admin Blood Test",
                "description": "Admin created test",
                "price": "699.00",
            },
            format="json",
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
    
        self.assertEqual(
            response.data["name"],
            "Admin Blood Test",
        )
    
        self.assertEqual(
            float(response.data["price"]),
            699.00,
        )
    
    def test_normal_user_cannot_update_test(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        response = self.client.patch(
            f"/api/tests/{self.test.id}/",
            {
                "name": "Modified Blood Test",
            },
            format="json",
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    
    def test_normal_user_cannot_delete_test(self):
        self.client.force_authenticate(
            user=self.user
        )
    
        response = self.client.delete(
            f"/api/tests/{self.test.id}/"
        )
    
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
    


    def test_admin_can_update_test(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f"/api/tests/{self.test.id}/",
            {
                "name": "Updated Blood Test",
                "price": "599.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Blood Test")
        self.assertEqual(float(response.data["price"]), 599.00)

    def test_admin_can_delete_test(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f"/api/tests/{self.test.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            DiagnosticTest.objects.filter(id=self.test.id).exists()
        )
    