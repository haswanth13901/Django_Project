from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from django.http import JsonResponse
from rest_framework.pagination import PageNumberPagination

from .models import Doctor, Appointment
from .serializers import DoctorSerializer, AppointmentSerializer
from .tasks import send_confirmation_email


def api_root(request):
    return JsonResponse({
        "create": "/api/create/",
        "filter": "/api/doctors/filter/"
    })


class DoctorCreateView(generics.CreateAPIView):
    queryset = Doctor.objects.all
    serializer_class = DoctorSerializer


class DoctorListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)


class DoctorPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class DoctorFilterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Delegate filtering and sorting to model layer
        queryset = Doctor.objects.filter_from_params(request.query_params)

        paginator = DoctorPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = DoctorSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DoctorDetailView(APIView):
    """
    Returns a FHIR Practitioner. We first try the model's to_fhir() helper.
    If that fails due to invalid fields (e.g., 'specialty' on Practitioner),
    we fall back to a sanitized Practitioner that maps specialization into
    'qualification.code.coding' (FHIR-correct) and NEVER includes 'specialty'.
    """
    permission_classes = [AllowAny]

    def get(self, request, practitioner_id):
        try:
            doctor = Doctor.objects.get(practitioner_id=practitioner_id)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1) Try the model helper first (your current path)
        try:
            fhir_resource = doctor.to_fhir()  # may raise Pydantic validation error
            # fhir.resources uses pydantic; .dict() -> JSON-ready dict
            return Response(fhir_resource.dict())
        except Exception as e:
            # 2) Fallback: build a clean Practitioner without 'specialty'
            #    and optionally map your specialization to qualification
            #    to keep the UI data available.
            sanitized = {
                "resourceType": "Practitioner",
                "id": str(doctor.practitioner_id),
                "name": [{
                    "family": (doctor.last_name or ""),
                    "given": [x for x in [doctor.first_name] if x] or [""],
                }],
                "telecom": [],
            }

            # Add telecom safely
            phone = getattr(doctor, "phone", None)
            if phone:
                sanitized["telecom"].append({"system": "phone", "value": str(phone)})
            email = getattr(doctor, "email", None)
            if email:
                sanitized["telecom"].append({"system": "email", "value": str(email)})

            # Optional common fields if you store them
            gender = getattr(doctor, "gender", None)
            if gender:
                sanitized["gender"] = str(gender)

            # ✅ Map specialization into qualification instead of invalid 'specialty'
            specialization_display = getattr(doctor, "specialization", None)
            specialization_code = getattr(doctor, "specialization_code", None) or (
                str(specialization_display).upper().replace(" ", "_") if specialization_display else None
            )
            if specialization_display:
                sanitized["qualification"] = [{
                    "code": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/practitioner-role",
                            "code": specialization_code,
                            "display": str(specialization_display),
                        }]
                    }
                }]

            # Optionally include address, birthDate, etc., if you have them

            # Also send back the reason we sanitized (useful for debugging)
            return Response(
                {
                    **sanitized,
                    "_note": "Returned sanitized Practitioner without 'specialty'; original to_fhir() failed: {}".format(str(e)),
                },
                status=status.HTTP_200_OK,
            )


class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            doctor = appointment.doctor

            # fire-and-forget confirmation email (Celery)
            send_confirmation_email.delay(
                patient_email=appointment.email,
                doctor_name=f"{doctor.first_name} {doctor.last_name}",
                appointment_date=str(appointment.appointment_date),
                appointment_time=str(appointment.appointment_time),
                appointment_id=str(appointment.appointment_id),
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
