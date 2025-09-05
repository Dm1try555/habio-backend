from django.db import models

class Channel(models.Model):
    TYPE_CHOICES = [
        ("call", "Call"),
        ("callback", "Callback"),
        ("messenger", "Messenger"),
        ("chat", "Chat"),
        ("form", "Form"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    label = models.CharField(max_length=100)
    link = models.CharField(max_length=200, blank=True, null=True)
    online_policy = models.CharField(max_length=100, blank=True, null=True)
    show_in_top = models.BooleanField(default=False)

    def __str__(self):
        return self.label

class Lead(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
