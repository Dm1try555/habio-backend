from django.db import models
from projects.models import Project
from channels.models import Channel


class Lead(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='leads')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    utm_source = models.CharField(max_length=100, blank=True, null=True)
    utm_medium = models.CharField(max_length=100, blank=True, null=True)
    utm_campaign = models.CharField(max_length=100, blank=True, null=True)
    page_url = models.URLField(blank=True, null=True)
    client_id = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=10, default='en')
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Lead {self.contact}"


class CallbackRequest(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='callbacks')
    phone = models.CharField(max_length=20)
    preferred_time = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    page_url = models.URLField(blank=True, null=True)
    utm_source = models.CharField(max_length=100, blank=True, null=True)
    utm_medium = models.CharField(max_length=100, blank=True, null=True)
    utm_campaign = models.CharField(max_length=100, blank=True, null=True)
    client_id = models.CharField(max_length=100, blank=True, null=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Callback {self.phone}"
