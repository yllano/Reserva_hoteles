from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    security_question = models.CharField(max_length=255, blank=True, default='')
    security_answer = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"Perfil de {self.user.username}"
