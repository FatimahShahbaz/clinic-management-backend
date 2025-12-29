from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import SignupSerializer
from .models import Doctor, User, Appointment
from datetime import datetime

class PatientAppointmentsView(APIView):
    def get(self, request, patient_id):
        # Fetch appointments for the patient from the database
        appointments = Appointment.objects.filter(patient_id=patient_id).order_by('-date', '-time')
        
        # Serialize into JSON-friendly format
        data = [
            {
                "id": apt.id,
                "doctor_name": apt.doctor_name,
                "date": str(apt.date),
                "time": str(apt.time),
                "reason": apt.reason,
            }
            for apt in appointments
        ]
        return Response(data)

class MyAppointmentsView(APIView):
    def get(self, request):
        # Get patient_id from query params
        patient_id = request.GET.get("patient_id")
        if not patient_id:
            return Response({"error": "Patient ID required"}, status=400)
        
        # Fetch all appointments for this patient
        appointments = Appointment.objects.filter(patient_id=patient_id)
        data = [
            {
                "id": apt.id,
                "doctor_name": apt.doctor_name,
                "date": str(apt.date),
                "time": str(apt.time),
                "reason": apt.reason,
                "status": getattr(apt, "status", "confirmed")  # default to confirmed
            }
            for apt in appointments
        ]
        return Response(data)



@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # If user is doctor, create doctor profile
            if user.category == "doctor":
                try:
                    Doctor.objects.create(
                        user=user,
                        specialty=request.data.get("specialty", "General"),
                        fee=request.data.get("fee", "PKR 2000"),
                        slots=[]
                    )
                except Exception as e:
                    return Response(
                        {"error": f"Doctor creation failed: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({
            "username": user.username,
            "role": user.category.lower(),
            "token": "dummy-token-for-now"  # your old token-style response
        }, status=status.HTTP_200_OK)


class DoctorSlotsView(APIView):
    # permission_classes = [IsAuthenticated]  # remove this

    def get(self, request):
        # fetch a doctor just for testing
        doctor = Doctor.objects.first()
        if not doctor:
            return Response({"error": "Doctor not found"}, status=404)
        return Response({"slots": doctor.slots})

    def post(self, request):
        doctor = Doctor.objects.first()
        if not doctor:
            return Response({"error": "Doctor not found"}, status=404)

        new_slot = request.data.get("slot")
        if not new_slot or "date" not in new_slot or "time" not in new_slot:
            return Response({"error": "Slot must have date and time"}, status=400)

        if doctor.slots is None:
            doctor.slots = []

        if new_slot in doctor.slots:
            return Response({"error": "Slot already exists"}, status=400)

        doctor.slots.append(new_slot)
        doctor.save()
        return Response({"slots": doctor.slots})
class DoctorListView(APIView):
    # Remove IsAuthenticated so it’s public
    def get(self, request):
        doctors = Doctor.objects.all()
        data = [
            {
                "id": doctor.user.id,
                "name": doctor.user.username,
                "specialty": doctor.specialty,
                "fee": doctor.fee,
                "slots": doctor.slots,
            }
            for doctor in doctors
        ]
        return Response(data)

class DoctorSlotsPublicView(APIView):
    # No authentication required
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            return Response({
                "slots": doctor.slots,
                "fee": doctor.fee,
                "specialty": doctor.specialty
            })
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=404)


class BookAppointmentView(APIView):
    def post(self, request):
        user = request.user
        if user.category != "patient":
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        doctor_id = request.data.get("doctor_id")
        date = request.data.get("date")
        time = request.data.get("time")
        reason = request.data.get("reason", "")

        if not doctor_id or not date or not time:
            return Response({"error": "Doctor, date, and time are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create appointment
        appointment = Appointment.objects.create(
            patient=user,
            doctor=doctor,
            date=date,
            time=time,
            reason=reason
        )

        return Response({
            "message": "Appointment booked successfully",
            "appointment_id": appointment.id
        }, status=status.HTTP_201_CREATED)
