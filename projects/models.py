from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='UTC')
    webhook_url = models.URLField(blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
