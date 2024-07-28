import datetime as dt

from datacenter.models import (
    Appointment,
    SpecialistWorkDayInSalon,
)


def get_first_time_slot(duty):
    time_now_hour = dt.datetime.now().hour
    time_now_minute = dt.datetime.now().minute
    if time_now_minute > 30:
        time_now = dt.datetime.combine(
            dt.date.today(), dt.time(time_now_hour + 1, 0)
        )
    else:
        time_now = dt.datetime.combine(
            dt.date.today(), dt.time(time_now_hour, 30)
        )

    duty_start_time = dt.datetime.combine(duty.workday, duty.start_at)
    duty_end_time = dt.datetime.combine(duty.workday, duty.end_at)

    if time_now < duty_start_time:
        first_time_slot = duty_start_time
    elif duty_start_time <= time_now < duty_end_time:
        first_time_slot = time_now
    else:
        first_time_slot = None

    return first_time_slot


def is_time_slot_busy(time_slot, appointments, service_duration):
    for appoinment in appointments:
        appoinment_start_time = dt.datetime.combine(
            appoinment.date, appoinment.start_at
        )
        appoinment_end_time = appoinment_start_time + service_duration
        if appoinment_start_time <= time_slot < appoinment_end_time:
            return True
    return False


def get_salons_and_times(specialist, service, date, salon=None):
    if salon:
        specialist_duties = SpecialistWorkDayInSalon.objects.filter(
            specialist=specialist,
            services=service,
            workday__range=(date, date + dt.timedelta(days=7)),
            salon=salon
        )
    else:
        specialist_duties = SpecialistWorkDayInSalon.objects.filter(
            specialist=specialist,
            services=service,
            workday__range=(date, date + dt.timedelta(days=7))
        )

    service_duration = dt.timedelta(minutes=service.duration)
    context = []
    for duty in specialist_duties:
        appointments = Appointment.objects.filter(
            specialist=specialist,
            service=service,
            date=duty.workday,
            salon=duty.salon
        ).exclude(status__in=["discard", "ended"])

        duty_end_time = dt.datetime.combine(duty.workday, duty.end_at)

        free_time_slots = []
        time_slot = get_first_time_slot(duty)
        while time_slot + service_duration < duty_end_time:
            if not is_time_slot_busy(
                    time_slot, appointments, service_duration
                ):
                free_time_slots.append(f"{time_slot.hour:02}:{time_slot.minute:02}")
            time_slot += service_duration

        context.append({
            "date": str(duty.workday),
            "salon_title": duty.salon.title,
            "salon_address": duty.salon.address,
            "free_times": free_time_slots,
        })

    return context
