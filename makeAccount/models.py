from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
class Appointment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE  # ensures appointment is deleted if doctor is deleted
    )
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.user.username} on {self.date}"


class DoctorSlot(models.Model):
    doctor = models.ForeignKey(
        'Doctor', 
        on_delete=models.CASCADE, 
        related_name='doctor_slots'  # <-- change from 'slots' to 'doctor_slots'
    )
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'date', 'time')

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} {self.time}"


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    specialty = models.CharField(max_length=100)
    fee = models.CharField(max_length=20)
    slots = models.JSONField(default=list, blank=True)  # list of available date/time slots

    def __str__(self):
        return self.user.username


class User(AbstractUser):
    CATEGORY_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    phone = models.CharField(max_length=15)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.username
