from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import User, Doctor, Patient, Appointment, Bill, MedicalRecord, Feedback, DoctorSlot
from .serializers import (
    SignupSerializer, UserSerializer, DoctorSerializer, PatientSerializer,
    AppointmentSerializer, BillSerializer, MedicalRecordSerializer, FeedbackSerializer
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        extra_info = {}
        if user.category == "patient":
            try:
                extra_info["patient_id"] = user.patient_profile.id
            except: pass
        elif user.category == "doctor":
            try:
                extra_info["doctor_id"] = user.doctor_profile.id
            except: pass

        return Response({
            "username": user.username,
            "role": user.category.lower(),
            "token": "dummy-token",
            "user_id": user.id,
            **extra_info
        }, status=status.HTTP_200_OK)

class DoctorListView(APIView):
    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class DoctorProfileView(APIView):
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=404)

    def put(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            if 'specialty' in request.data:
                doctor.specialty = request.data['specialty']
            if 'fee' in request.data:
                doctor.fee = request.data['fee']
            if 'username' in request.data:
                doctor.user.username = request.data['username']
            if 'phone' in request.data:
                doctor.user.phone = request.data['phone']
            
            doctor.user.save()
            doctor.save()
            
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=404)

class PatientListView(APIView):
    def get(self, request):
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

class DoctorServedPatientsView(APIView):
    def get(self, request, doctor_id):
        patient_ids = Appointment.objects.filter(
            doctor_id=doctor_id, 
            status='completed'
        ).values_list('patient_id', flat=True).distinct()
        patients = Patient.objects.filter(user_id__in=patient_ids)
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

class AppointmentListView(APIView):
    def get(self, request):
        appointments = Appointment.objects.all().order_by('-date', '-time')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class AppointmentDeleteView(APIView):
    def delete(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Reset the slot if it exists
            try:
                slot = DoctorSlot.objects.get(
                    doctor=appointment.doctor,
                    date=appointment.date,
                    time=appointment.time
                )
                slot.is_booked = False
                slot.save()
            except DoctorSlot.DoesNotExist:
                pass

            appointment.delete()
            return Response({"message": "Appointment deleted successfully"}, status=200)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class DoctorSlotsView(APIView):
    def get(self, request):
        doctor_id = request.GET.get("doctor_id")
        try:
            if not doctor_id:
                slots = DoctorSlot.objects.all().order_by('-date', '-time')
                return Response({"slots": [{"id": s.id, "doctor_name": s.doctor.user.username, "date": str(s.date), "time": str(s.time), "is_booked": s.is_booked} for s in slots]})
            else:
                try:
                    doctor = Doctor.objects.get(id=doctor_id)
                except:
                    doctor = User.objects.get(id=doctor_id).doctor_profile
                
                slots = DoctorSlot.objects.filter(doctor=doctor).order_by('-date', '-time')
                return Response({"slots": [{"id": s.id, "date": str(s.date), "time": str(s.time), "is_booked": s.is_booked} for s in slots]})
        except Exception as e:
            return Response({"error": str(e), "slots": []}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            doctor_id = request.data.get("doctor_id") or request.GET.get("doctor_id")
            if not doctor_id:
                doctor = Doctor.objects.first()
            else:
                try:
                    doctor = Doctor.objects.get(id=doctor_id)
                except:
                    doctor = User.objects.get(id=doctor_id).doctor_profile
            
            slot_data = request.data.get("slot")
            if not slot_data:
                return Response({"error": "No slot data"}, status=400)
            
            slot = DoctorSlot.objects.create(
                doctor=doctor,
                date=slot_data["date"],
                time=slot_data["time"]
            )
            return Response({"slot": {"id": slot.id, "date": str(slot.date), "time": str(slot.time), "is_booked": slot.is_booked}})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DoctorSlotsPublicView(APIView):
    def get(self, request, doctor_id):
        try:
            try:
                 doctor = User.objects.get(id=doctor_id).doctor_profile
            except:
                 doctor = Doctor.objects.get(id=doctor_id)
            
            slots = DoctorSlot.objects.filter(doctor=doctor, is_booked=False)
            return Response({
                "slots": [{"date": str(s.date), "time": str(s.time)} for s in slots],
                "fee": doctor.fee,
                "specialty": doctor.specialty
            })
        except:
            return Response({"error": "Doctor not found"}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class AppointmentCreateView(APIView):
    def post(self, request):
        doctor_id = request.data.get("doctor")
        date_str = request.data.get("date")
        time_str = request.data.get("time")

        try:
            slot = DoctorSlot.objects.get(doctor_id=doctor_id, date=date_str, time=time_str)
            if slot.is_booked:
                return Response({"error": "This slot is already booked"}, status=400)
        except DoctorSlot.DoesNotExist:
            pass 

        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            
            try:
                slot = DoctorSlot.objects.get(doctor_id=doctor_id, date=date_str, time=time_str)
                slot.is_booked = True
                slot.save()
            except DoctorSlot.DoesNotExist:
                pass

            try:
                fee_val = 2000
                import re
                match = re.search(r'\d+', appointment.doctor.fee)
                if match:
                    fee_val = float(match.group())
                Bill.objects.create(appointment=appointment, amount=fee_val)
            except:
                Bill.objects.create(appointment=appointment, amount=2000)
            return Response({"message": "Appointment booked successfully", "appointment": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class AppointmentUpdateView(APIView):
    def put(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            status_val = request.data.get("status")
            if status_val:
                old_status = appointment.status
                appointment.status = status_val
                appointment.save()

                if status_val == "cancelled" and old_status != "cancelled":
                    try:
                        slot = DoctorSlot.objects.get(
                            doctor=appointment.doctor, 
                            date=appointment.date, 
                            time=appointment.time
                        )
                        slot.is_booked = False
                        slot.save()
                    except DoctorSlot.DoesNotExist:
                        pass

                return Response({"message": f"Appointment marked as {status_val}"})
            return Response({"error": "Status required"}, status=400)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=404)

class PatientAppointmentsView(APIView):
    def get(self, request, patient_id):
        appointments = Appointment.objects.filter(patient_id=patient_id).order_by('-date', '-time')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

class DoctorAppointmentsView(APIView):
    def get(self, request, doctor_id):
        appointments = Appointment.objects.filter(doctor_id=doctor_id).order_by('-date', '-time')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

class DoctorStatsView(APIView):
    def get(self, request, doctor_id):
        appointments = Appointment.objects.filter(doctor_id=doctor_id)
        return Response({
            "total_appointments": appointments.count(),
            "completed_appointments": appointments.filter(status='completed').count(),
            "pending_appointments": appointments.filter(status='confirmed').count(),
            "total_patients": Appointment.objects.filter(doctor_id=doctor_id, status='completed').values('patient').distinct().count()
        })

@method_decorator(csrf_exempt, name='dispatch')
class FeedbackCreateView(APIView):
    def post(self, request):
        patient_id = request.data.get("patient_id")
        content = request.data.get("content")
        if not patient_id or not content:
            return Response({"error": "Missing data"}, status=400)
        Feedback.objects.create(patient_id=patient_id, content=content)
        return Response({"message": "Feedback submitted"})

class BillListView(APIView):
    def get(self, request):
        patient_id = request.GET.get("patient_id")
        if patient_id:
            bills = Bill.objects.filter(appointment__patient_id=patient_id)
        else:
            bills = Bill.objects.all().order_by('-created_at')
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class BillPayView(APIView):
    def put(self, request, bill_id):
        try:
            bill = Bill.objects.get(id=bill_id)
            bill.status = 'paid'
            bill.save()
            return Response({"message": "Paid successfully"})
        except Bill.DoesNotExist:
            return Response({"error": "Bill not found"}, status=404)

class MedicalRecordView(APIView):
    def get(self, request):
        patient_id = request.GET.get("patient_id")
        if patient_id:
            try:
                 records = MedicalRecord.objects.filter(patient__id=patient_id).order_by('-date')
            except:
                 records = MedicalRecord.objects.filter(patient__user_id=patient_id).order_by('-date')
        else:
            records = MedicalRecord.objects.all().order_by('-date')
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MedicalRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminStatsView(APIView):
    def get(self, request):
        return Response({
            "total_users": User.objects.count(),
            "total_doctors": Doctor.objects.count(),
            "total_patients": Patient.objects.count(),
            "total_appointments": Appointment.objects.count(),
            "total_revenue": sum(float(b.amount) for b in Bill.objects.filter(status='paid'))
        })

class UserManagementView(APIView):
    def get(self, request):
        users = User.objects.all().order_by('-id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class UserDetailView(APIView):
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except User.DoesNotExist:
             return Response(status=404)
    
    def delete(self, request, pk):
        try:
            User.objects.get(pk=pk).delete()
            return Response(status=204)
        except User.DoesNotExist:
             return Response(status=404)

