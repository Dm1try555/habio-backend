from django.db import models
from django.contrib.auth.models import User

class ProjectConfig(models.Model):
    name = models.CharField(max_length=100)
    timezone = models.CharField(max_length=50, default='UTC')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Channel(models.Model):
    TYPE_CHOICES = [
        ("call", "Call"),
        ("callback", "Callback"),
        ("messenger", "Messenger"),
        ("chat", "Chat"),
        ("form", "Form"),
    ]
    
    project = models.ForeignKey(ProjectConfig, on_delete=models.CASCADE, related_name='channels')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    label = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Номер телефона для каналов типа 'call'")
    online_policy = models.CharField(max_length=100, blank=True, null=True)
    show_in_top = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['priority', 'id']

    def __str__(self):
        return f"{self.project.name} - {self.label}"

class Schedule(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    project = models.ForeignKey(ProjectConfig, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working_day = models.BooleanField(default=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.project.name} - {self.get_day_display()} {self.start_time}-{self.end_time}"

class Lead(models.Model):
    project = models.ForeignKey(ProjectConfig, on_delete=models.CASCADE, related_name='leads')
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
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead from {self.channel.label} - {self.contact}"

class CallbackRequest(models.Model):
    project = models.ForeignKey(ProjectConfig, on_delete=models.CASCADE, related_name='callbacks')
    phone = models.CharField(max_length=20)
    preferred_time = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    page_url = models.URLField(blank=True, null=True)
    utm_source = models.CharField(max_length=100, blank=True, null=True)
    utm_medium = models.CharField(max_length=100, blank=True, null=True)
    utm_campaign = models.CharField(max_length=100, blank=True, null=True)
    client_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Callback request - {self.phone}"

class ChatSession(models.Model):
    project = models.ForeignKey(ProjectConfig, on_delete=models.CASCADE, related_name='chat_sessions')
    client_id = models.CharField(max_length=100)
    page_url = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat session {self.id} - {self.client_id}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
