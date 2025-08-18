import uuid
from django.db import models
from django.db.models import Q
from fhir.resources.practitioner import Practitioner
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint


class DoctorQuerySet(models.QuerySet):
    def apply_filters(self, params):
        """
        Apply filtering based on expected query params.
        Accepts any dict-like (e.g., Django QueryDict).
        """
        qs = self

        doctor_id = params.get("id")
        first_name = params.get("first_name")
        last_name = params.get("last_name")
        specialization = params.get("specialization")
        city = params.get("city")
        state = params.get("state")
        zip_code = params.get("zip_code")

        filters = {}
        if doctor_id:
            filters["practitioner_id__iexact"] = doctor_id
        if specialization:
            filters["specialization__icontains"] = specialization
        if city:
            filters["city__icontains"] = city
        if state:
            filters["state__icontains"] = state
        if zip_code:
            filters["zip_code__icontains"] = zip_code

        if filters:
            qs = qs.filter(**filters)

        if first_name or last_name:
            name_filter = Q()
            if first_name:
                name_filter |= Q(first_name__icontains=first_name)
            if last_name:
                name_filter |= Q(last_name__icontains=last_name)
            qs = qs.filter(name_filter)

        return qs

    def order_by_name(self, sort: str = "asc"):
        if str(sort).lower() == "desc":
            return self.order_by("-first_name", "-last_name")
        return self.order_by("first_name", "last_name")


class DoctorManager(models.Manager.from_queryset(DoctorQuerySet)):
    def filter_from_params(self, params, default_sort: str = "asc"):
        """
        Convenience one-liner used by views.
        """
        sort = params.get("sort", default_sort)
        return self.get_queryset().apply_filters(params).order_by_name(sort)


class Doctor(models.Model):
    practitioner_id = models.CharField(max_length=50, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    objects = DoctorManager()

    class Meta:
        db_table = "doctors"
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["state"]),
            models.Index(fields=["zip_code"]),
            models.Index(fields=["specialization"]),
        ]

    def validate_fields(self):
        errors = []

        if not self.first_name or not self.last_name:
            errors.append("First name and last name are required.")
        if not self.phone:
            errors.append("Phone number is required.")
        if self.phone and len(self.phone) < 10:
            errors.append("Phone number must be at least 10 digits.")
        if not self.specialization:
            errors.append("Specialization is required.")
        if not self.address:
            errors.append("Address is required.")

        return errors

    def to_fhir(self):
        validation_errors = self.validate_fields()
        if validation_errors:
            raise ValueError("Validation failed: " + ", ".join(validation_errors))

        practitioner = Practitioner.construct()
        practitioner.id = self.practitioner_id
        practitioner.name = [HumanName(use="official", family=self.last_name, given=[self.first_name])]
        practitioner.telecom = [ContactPoint(system="phone", value=self.phone)]
        practitioner.address = [Address(line=[self.address], city=self.city, state=self.state, postalCode=self.zip_code)]
        practitioner.specialty = [
            {"coding": [{"system": "http://hl7.org/fhir/specialty", "code": self.specialization}]}
        ]

        return practitioner

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.specialization})"


class Appointment(models.Model):
    appointment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, related_name="appointments")
    patient_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    reason = models.TextField()
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "appointment_date", "appointment_time")
        ordering = ["appointment_date", "appointment_time"]

    def __str__(self):
        return f"{self.patient_name} - {self.doctor} on {self.appointment_date} at {self.appointment_time}"
