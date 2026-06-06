

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('mod', 'Moderator'),
        ('user', 'Użytkownik'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)
    is_online = models.BooleanField(default=False)

    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.username