from django.db import models


class User(models.Model):
    name = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(default=None, null=True)
    birthday = models.DateField(default=None, null=True)
    usergroup = models.CharField(default='user', max_length=255)
