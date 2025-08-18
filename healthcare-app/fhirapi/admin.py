from django.contrib import admin
from .models import Doctor, Appointment

class NameListFilter(admin.SimpleListFilter):
    title = 'Name'
    parameter_name = 'name'

    def lookups(self, request, model_admin):
        names = (
            Doctor.objects
            .values_list('first_name', 'last_name')
            .distinct()
            .order_by('first_name')[:100]
        )
        return [
            (f"{first} {last}", f"{first} {last}")
            for first, last in names if first and last
        ]

    def queryset(self, request, queryset):
        if self.value():
            parts = self.value().split(" ", 1)
            if len(parts) == 2:
                return queryset.filter(first_name=parts[0], last_name=parts[1])
        return queryset

class CityListFilter(admin.SimpleListFilter):
    title = 'City'
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = (
            Doctor.objects
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')[:100]
        )
        return [(city, city) for city in cities if city]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city=self.value())
        return queryset

class StateListFilter(admin.SimpleListFilter):
    title = 'State'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        states = (
            Doctor.objects
            .values_list('state', flat=True)
            .distinct()
            .order_by('state')[:100]
        )
        return [(state, state) for state in states if state]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state=self.value())
        return queryset

class ZipCodeListFilter(admin.SimpleListFilter):
    title = 'Zip Code'
    parameter_name = 'zip_code'

    def lookups(self, request, model_admin):
        zips = (
            Doctor.objects
            .values_list('zip_code', flat=True)
            .distinct()
            .order_by('zip_code')[:100]
        )
        return [(z, z) for z in zips if z]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(zip_code=self.value())
        return queryset

class SpecializationListFilter(admin.SimpleListFilter):
    title = 'Specialization'
    parameter_name = 'specialization'

    def lookups(self, request, model_admin):
        specs = (
            Doctor.objects
            .values_list('specialization', flat=True)
            .distinct()
            .order_by('specialization')[:100]
        )
        return [(spec, spec) for spec in specs if spec]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(specialization=self.value())
        return queryset

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'practitioner_id', 'first_name', 'last_name',
        'specialization', 'city', 'state', 'zip_code', 'phone'
    )
    search_fields = (
        'practitioner_id', 'first_name', 'last_name',
        'specialization', 'city', 'state', 'zip_code'
    )
    list_filter = (
        NameListFilter,
        SpecializationListFilter,
        StateListFilter,
        CityListFilter,
        ZipCodeListFilter,
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'appointment_id', 'doctor', 'patient_name',
        'appointment_date', 'appointment_time', 'created_at'
    )
    search_fields = (
        'appointment_id', 'patient_name', 'phone_number', 'email', 'doctor__first_name', 'doctor__last_name'
    )
    list_filter = (
        'appointment_date', 'doctor__specialization', 'doctor__city'
    )
    readonly_fields = ('appointment_id', 'created_at')
