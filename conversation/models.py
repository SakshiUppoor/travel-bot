from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.


class ChatMessage(models.Model):
    timestamp = models.DateTimeField(default=datetime.now)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="from_user", null=True)
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="to_user", null=True)
    text = models.CharField(max_length=128)

    def __str__(self):
        return self.text + ' FROM:' + self.from_user.username + ' TO:' + self.to_user.username


class Booking(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer", null=True)
    noOfRooms = models.IntegerField(default=0, null=True)
    checkInDate = models.DateField(null=True)
    checkOutDate = models.DateField(null=True)
    destination = models.CharField(max_length=128, null=True)
    completed = models.BooleanField(default=False)
