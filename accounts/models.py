from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(
        self, username, full_name, phone_number, password=None, **extra_fields
    ):
        if not username:
            raise ValueError("The Username field must be set")

        user = self.model(
            username=username,
            full_name=full_name,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, full_name, phone_number, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            username, full_name, phone_number, password, **extra_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    call_back_time = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name", "phone_number"]

    def __str__(self):
        return self.username
