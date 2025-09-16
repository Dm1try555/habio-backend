from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = None  
    email = models.EmailField(unique=True)

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('marketing', 'Marketing'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
    ]
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []       

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.role})"
