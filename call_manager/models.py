from django.db import models
from accounts.models import CustomUser


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)


class Recipient(models.Model):
    CALL_STATUSES = (
        ("waiting", "Waiting"),
        ("done", "Done"),
        ("refused", "Refused"),
        ("invalid", "Invalid Number"),
        ("call_back", "Call Back"),
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    items_received = models.ManyToManyField(Item)
    call_status = models.CharField(
        max_length=15, choices=CALL_STATUSES, default="waiting"
    )

    state = models.TextField(blank=True, null=True)
    place = models.TextField(blank=True, null=True)

    date_distribution = models.DateField(blank=True, null=True)

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    gender = models.CharField(
        max_length=6, choices=GENDER_CHOICES, blank=True, null=True
    )

    age = models.PositiveIntegerField(blank=True, null=True)
    volunteer = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    done_at = models.DateTimeField(blank=True, null=True)
    last_updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_recipients",
    )
    call_back_time = models.DateTimeField(blank=True, null=True)
