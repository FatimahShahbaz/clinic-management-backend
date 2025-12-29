from django.urls import path
from .views import SignupView
from .views import LoginView
from .views import BookAppointmentView
from .views import DoctorListView
from .views import DoctorSlotsView
from .views import DoctorSlotsPublicView
from .views import MyAppointmentsView
from .views import PatientAppointmentsView
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view() , name='login'),
    path("patient/book-appointment/", BookAppointmentView.as_view(), name="book-appointment"),
    path("doctors/", DoctorListView.as_view(), name="doctor-list"),
     path("doctor/slots/", DoctorSlotsView.as_view(), name="doctor-slots"),
     path("doctors/<int:doctor_id>/slots/", DoctorSlotsPublicView.as_view()),
    path("my-appointments/", MyAppointmentsView.as_view(), name="my-appointments"),
      path("patient/<int:patient_id>/appointments/", PatientAppointmentsView.as_view(), name="patient-appointments"),
]

