from django.db import models
from Catalog.models import *

class Notification(models.Model):
    class Status(models.TextChoices):
        SENT = 'sent'
        RECEIVED = 'received'
        RESOLVED = 'resolved'
        CANCELED = 'canceled'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='notification')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SENT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for Order #{self.order.pk} - {self.status}"