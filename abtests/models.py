from django.db import models
from projects.models import Project
from users.models import User


class ABTest(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ab_tests')
    traffic_percentage = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class ABTestVariant(models.Model):
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    channel_order = models.JSONField(default=list)
    copy_text = models.JSONField(default=dict)
    is_control = models.BooleanField(default=False)
    weight = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class UserVariant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='variants')
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE)
    variant = models.ForeignKey(ABTestVariant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'ab_test']
