from django.db import models
from projects.models import Project


class Channel(models.Model):
    TYPE_CHOICES = [
        ("call", "Call"),
        ("callback", "Callback"),
        ("messenger", "Messenger"),
        ("chat", "Chat"),
        ("form", "Form"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='channels')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    label = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    online_policy = models.CharField(max_length=100, blank=True, null=True)
    show_in_top = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', 'id']

    def __str__(self) -> str:
        return f"{self.project.name} - {self.label}"
