from django.db import models
from django.core.exceptions import ValidationError
import re

class Detector(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    loginId = models.CharField(max_length=50, unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    address = models.TextField()
    status = models.CharField(max_length=20, default='waiting')

    def __str__(self):
        return self.name

    def clean(self):
        # Validate name
        if not self.name or not self.name.strip():
            raise ValidationError("Name is required.")

        # Validate email using regex (even though EmailField checks format)
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, self.email):
            raise ValidationError("Enter a valid email address.")

        # Validate loginId (at least 5 characters, alphanumeric)
        if not re.match(r'^[A-Za-z0-9_]{5,}$', self.loginId):
            raise ValidationError("Login ID must be at least 5 characters and alphanumeric.")

        # Validate mobile number (e.g., 10-digit Indian format)
        if not re.match(r'^\d{10}$', self.mobile):
            raise ValidationError("Enter a valid 10-digit mobile number.")

        # Validate password (at least 8 characters, one uppercase, one lowercase, one number)
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'
        if not re.match(password_pattern, self.password):
            raise ValidationError(
                "Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, and one digit."
            )

        # Validate address
        if not self.address or not self.address.strip():
            raise ValidationError("Address is required.")
