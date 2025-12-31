from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile")
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE
    )
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def doctor_name(self):
        return self.doctor.user.username

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.user.username} on {self.date}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField(blank=True)
    tests = models.JSONField(default=list, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.patient.user.username} - {self.date}"


class Bill(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="bill")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('paid', 'Paid'), ('unpaid', 'Unpaid')], default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill {self.id} for {self.appointment}"


class Feedback(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.patient.username}"


class DoctorSlot(models.Model):
    doctor = models.ForeignKey(
        'Doctor', 
        on_delete=models.CASCADE, 
        related_name='doctor_slots'
    )
    date = models.DateField()
    time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('doctor', 'date', 'time')

    def __str__(self):
        return f"{self.doctor.user.username} - {self.date} {self.time} ({'Booked' if self.is_booked else 'Available'})"


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile")
    specialty = models.CharField(max_length=100)
    fee = models.CharField(max_length=20)
    slots = models.JSONField(default=list, blank=True)

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
