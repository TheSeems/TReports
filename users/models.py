from django.db import models

# Create your models here.
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, nick, password, **extra):
        """
        Create and save a User with the given email and password.
        """
        user = self.model(nick=nick, **extra)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, nick, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(nick, password, **extra_fields)


class Role(models.Model):
    priority = models.IntegerField()
    name = models.CharField(max_length=100)
    style = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email', unique=True, blank=True)
    role = models.ManyToManyField(Role)
    joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    nick = models.CharField(max_length=100, unique=True)

    USERNAME_FIELD = 'nick'
    objects = CustomUserManager()
