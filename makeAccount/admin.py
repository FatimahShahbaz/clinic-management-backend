from django.contrib import admin
from .models import User, Doctor, Patient, Appointment, Bill, MedicalRecord, Feedback, DoctorSlot

admin.site.register(User)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Bill)
admin.site.register(MedicalRecord)
admin.site.register(Feedback)
admin.site.register(DoctorSlot)
