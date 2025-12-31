from rest_framework import serializers
from .models import User, Doctor, DoctorSlot, Appointment, Patient, Bill, MedicalRecord, Feedback

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'category']

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Patient
        fields = ['id', 'user', 'gender', 'blood_group']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialty', 'fee', 'slots']

class DoctorSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSlot
        fields = ['id', 'doctor', 'date', 'time']

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField()
    class Meta:
        model = Appointment
        fields = ["id", "patient", "doctor", "date", "time", "reason", "status", "doctor_name"]

class BillSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='appointment.doctor.user.username')
    date = serializers.ReadOnlyField(source='appointment.date')
    class Meta:
        model = Bill
        fields = ['id', 'appointment', 'amount', 'status', 'doctor_name', 'date']

class MedicalRecordSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.user.username')
    class Meta:
        model = MedicalRecord
        fields = ['id', 'patient', 'doctor', 'diagnosis', 'prescription', 'notes', 'tests', 'date', 'doctor_name']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'patient', 'content', 'created_at']

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    gender = serializers.CharField(write_only=True, required=False)
    blood_group = serializers.CharField(write_only=True, required=False)
    specialty = serializers.CharField(write_only=True, required=False)
    fee = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'phone', 'category', 'gender', 'blood_group', 'specialty', 'fee']

    def create(self, validated_data):
        gender = validated_data.pop('gender', None)
        blood_group = validated_data.pop('blood_group', None)
        specialty = validated_data.pop('specialty', None)
        fee = validated_data.pop('fee', None)
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        if user.category == 'doctor':
             Doctor.objects.create(user=user, specialty=specialty or "General", fee=fee or "PKR 2000")
        elif user.category == 'patient':
             Patient.objects.create(user=user, gender=gender or "Other", blood_group=blood_group or "N/A")
             
        return user
