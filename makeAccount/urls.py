from django.urls import path
from .views import (
    SignupView, LoginView, DoctorListView, PatientListView, AppointmentListView,
    DoctorSlotsView, DoctorSlotsPublicView, AppointmentCreateView, AppointmentUpdateView,
    AppointmentDeleteView, PatientAppointmentsView, DoctorAppointmentsView, FeedbackCreateView,
    BillListView, BillPayView, MedicalRecordView, AdminStatsView,
    UserManagementView, UserDetailView, DoctorProfileView, DoctorStatsView,
    DoctorServedPatientsView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view() , name='login'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctor/<int:doctor_id>/', DoctorProfileView.as_view(), name='doctor-profile'),
    path('doctor/<int:doctor_id>/stats/', DoctorStatsView.as_view(), name='doctor-stats'),
    path('doctor/<int:doctor_id>/served-patients/', DoctorServedPatientsView.as_view(), name='served-patients'),
    path('patients/', PatientListView.as_view(), name='patient-list'),
    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/<int:appointment_id>/update/', AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/<int:appointment_id>/delete/', AppointmentDeleteView.as_view(), name='appointment-delete'),
    path('doctor/slots/', DoctorSlotsView.as_view(), name='doctor-slots'),
    path('doctor/<int:doctor_id>/slots/', DoctorSlotsPublicView.as_view(), name='doctor-slots-public'),
    path('appointments/create/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('patient/<int:patient_id>/appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('doctor/<int:doctor_id>/appointments/', DoctorAppointmentsView.as_view(), name='doctor-appointments'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('bills/', BillListView.as_view(), name='bill-list'),
    path('bills/<int:bill_id>/pay/', BillPayView.as_view(), name='bill-pay'),
    path('medical-records/', MedicalRecordView.as_view(), name='medical-record-list'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/users/', UserManagementView.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
]
