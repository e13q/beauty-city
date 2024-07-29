import datetime as dt
from datacenter.models import (
    Service,
    Salon,
    Specialist,
    Appointment,
    SpecialistWorkDayInSalon
)


def get_all_salons():
    return Salon.objects.all()


def get_salon(id):
    return Salon.objects.get(pk=id)


def get_all_services():
    return Service.objects.all()


def get_services_by_workdays(workdays):
    if not workdays:
        return None
    services_list = []
    for workday in workdays:
        [services_list.append(
            service.id
        ) for service in workday.services.all()]
    services_list = list(dict.fromkeys(services_list))
    services_arr = []
    for service_id in services_list:
        service = get_service(service_id)
        services_arr.append({
            'id': service_id, 'title': service.title, 'price': service.price
            }
        )
    return services_arr


def get_services_by_specialist(specialist_id):
    date = dt.datetime.now()
    specialist = get_specialist(specialist_id)
    workdays = SpecialistWorkDayInSalon.objects.filter(
        specialist=specialist,
        workday__range=(date, date + dt.timedelta(days=7)),
    )
    return get_services_by_workdays(workdays)


def get_services_by_salon(salon_id):
    date = dt.datetime.now()
    salon = get_salon(salon_id)
    workdays = SpecialistWorkDayInSalon.objects.filter(
        salon=salon,
        workday__range=(date, date + dt.timedelta(days=7)),
    )
    return get_services_by_workdays(workdays)


def get_service(id):
    return Service.objects.get(pk=id)


def get_all_specialists():
    return Specialist.objects.all()


def get_specialist(id):
    return Specialist.objects.get(pk=id)


def get_first_time_slot(duty):
    time_now_hour = dt.datetime.now().hour
    time_now_minute = dt.datetime.now().minute
    if time_now_minute > 30:
        time_now = dt.datetime.combine(
            dt.date.today(), dt.time(time_now_hour, 0)
        )
        time_now += dt.timedelta(hours=1)
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


def get_salons_and_times(service, salon=None, specialist=None):
    date = dt.datetime.now()
    if salon:
        specialist_duties = SpecialistWorkDayInSalon.objects.filter(
            services=service,
            workday__range=(date, date + dt.timedelta(days=7)),
            salon=salon
        )
    elif specialist:
        specialist_duties = SpecialistWorkDayInSalon.objects.filter(
            specialist=specialist,
            services=service,
            workday__range=(date, date + dt.timedelta(days=7))
        )
    else:
        specialist_duties = SpecialistWorkDayInSalon.objects.filter(
            services=service,
            workday__range=(date, date + dt.timedelta(days=7))
        )

    service_duration = dt.timedelta(minutes=service.duration)
    context = dict()
    context_salons = dict()
    for duty in specialist_duties:
        if not specialist:
            specialist = duty.specialist
        if not salon:
            salon = duty.salon
        appointments = Appointment.objects.filter(
            specialist=specialist,
            service=service,
            date=duty.workday,
            salon=salon
        ).exclude(status__in=["discard", "ended"])
        duty_end_time = dt.datetime.combine(duty.workday, duty.end_at)
        free_time_slots = []
        time_slot = get_first_time_slot(duty)
        if time_slot:
            while time_slot + service_duration < duty_end_time:
                if not is_time_slot_busy(
                        time_slot, appointments, service_duration
                ):
                    free_time_slots.append(
                        f"{time_slot.hour:02}:{time_slot.minute:02}")
                time_slot += service_duration
        context_salons[salon.title] = salon.address
        if not context.get(salon.title):
            context[salon.title] = {
                str(duty.workday): free_time_slots
            }
        else:
            context[salon.title].update({str(duty.workday): free_time_slots})
    return context, context_salons
