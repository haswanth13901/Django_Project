from django.urls import path
from .views import (
    api_root,
    DoctorCreateView,
    DoctorFilterView,
    DoctorListView,
    DoctorDetailView,  
)
from .views import AppointmentCreateView

urlpatterns = [
    path('', api_root),
    path('create/', DoctorCreateView.as_view(), name='doctor-create'),
    path('doctors/filter/', DoctorFilterView.as_view(), name='doctor-filter'),
    path('doctors/', DoctorListView.as_view(), name='doctor-list'),
    path('doctor/<int:practitioner_id>/', DoctorDetailView.as_view(), name='doctor-detail'),  
    path('appointments/create/', AppointmentCreateView.as_view(), name='create-appointment'),
]
