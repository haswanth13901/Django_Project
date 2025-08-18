from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_confirmation_email(patient_email, doctor_name, appointment_date, appointment_time, appointment_id):
    subject = "Appointment Confirmation"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [patient_email]

    context = {
        "Doctor_name": doctor_name,
        "Appointment_date": appointment_date,
        "Appointment_time": appointment_time,
        "Appointment_id": appointment_id,
    }

    text_content = render_to_string('emails/appointment_confirmation.txt', context)
    html_content = render_to_string('emails/appointment_confirmation.html', context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
