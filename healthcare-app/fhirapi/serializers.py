from rest_framework import serializers
from .models import Doctor, Appointment  
from fhir.resources.practitioner import Practitioner
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
import re 

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

    def to_fhir(self):
        doctor = self.instance
        practitioner = Practitioner.construct()

        practitioner.name = [HumanName(use="official", family=doctor.last_name, given=[doctor.first_name])]
        practitioner.telecom = [ContactPoint(system="phone", value=doctor.phone)]
        practitioner.address = [Address(line=[doctor.address])]
        practitioner.specialty = [{"coding": [{"system": "http://hl7.org/fhir/specialty", "code": doctor.specialization}]}]

        return practitioner

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.first_name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'appointment_id', 'doctor', 'doctor_name',
            'patient_name', 'phone_number', 'email', 'reason',
            'appointment_date', 'appointment_time'
        ]

    def validate_phone_number(self, value):
        import re
        if not re.match(r'^\+\d{10,15}$', value):
            raise serializers.ValidationError("Phone number must be in international format like +11234567890.")
        return value