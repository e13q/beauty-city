# import random
# import uuid
# from faker import Faker
from mybot.models import Client, Salon, Service, Specialist, Order, SpecialistWorkDayInSalon, Appointment


# # ! запуск через PowerShell команда - >>> exec(open("supplement_data.py", encoding="utf-8").read())


clients = [
    {"id_tg": 224, "full_name": "Иван", "phone_number": "+79699998121"},
    {"id_tg": 225, "full_name": "Мария", "phone_number": "+79686758122"},
    {"id_tg": 226, "full_name": "Христина", "phone_number": "+79622228123"},
    {"id_tg": 227, "full_name": "Кристина", "phone_number": "+79611118123"},
    {"id_tg": 228, "full_name": "Егор", "phone_number": "+79676448123"},
    {"id_tg": 229, "full_name": "Виталия", "phone_number": "+79612348123"},
    {"id_tg": 230, "full_name": "Виталий", "phone_number": "+79601588123"},
    {"id_tg": 231, "full_name": "Александр", "phone_number": "+79665968123"},
    {"id_tg": 232, "full_name": "Дарья", "phone_number": "+79634567123"},
    {"id_tg": 233, "full_name": "Светлана", "phone_number": "+79687998123"},
    {"id_tg": 234, "full_name": "Максим", "phone_number": "+79631238123"},
    {"id_tg": 235, "full_name": "Анна", "phone_number": "+79665828123"},
    {"id_tg": 236, "full_name": "Олег", "phone_number": "+79624356123"},
    {"id_tg": 237, "full_name": "Татьяна", "phone_number": "+79657899123"},
    {"id_tg": 238, "full_name": "Юлия", "phone_number": "+79681234123"},
    {"id_tg": 239, "full_name": "Дмитрий", "phone_number": "+79667587123"},
    {"id_tg": 240, "full_name": "Алина", "phone_number": "+79609877123"},
    {"id_tg": 241, "full_name": "Николай", "phone_number": "+79621432123"},
    {"id_tg": 242, "full_name": "Виктория", "phone_number": "+79632678123"},
    {"id_tg": 243, "full_name": "Константин", "phone_number": "+79643218123"}
]

client_objects = [Client.objects.create(**client) for client in clients]


salons = [
    {"title": "Tip-Top", "address": "г. Москва ул. Красноармейская, д. 1"},
    {"title": "Glamour", "address": "г. Москва ул. Ленина, д. 5"},
    {"title": "Beauty Plus", "address": "г. Москва ул. Тверская, д. 10"}
]

salon_objects = [Salon.objects.create(**salon) for salon in salons]


services = [
    {"title": "Окрашивание", "price": 4500.0, "duration": 180},
    {"title": "Маникюр", "price": 1500.0, "duration": 60},
    {"title": "Стрижка", "price": 2000.0, "duration": 90},
    {"title": "Педикюр", "price": 2500.0, "duration": 90}
]

service_objects = [Service.objects.create(**service) for service in services]


specialists = [
    {"full_name": "Иван Иван Иваныч"},
    {"full_name": "Петр Петрович"},
    {"full_name": "Мария Ивановна"},
    {"full_name": "Александр Ракшин"},
    {"full_name": "Ксения Кузнецова"},
    {"full_name": "Мария Петровна"},
    {"full_name": "Сергей Сергеевич"}
]

specialist_objects = [Specialist.objects.create(**specialist) for specialist in specialists]


orders = [
    {"client": client_objects[i], "status": status, "receipt": f'https://www.example.com/receipt{i}'}
    for i, status in enumerate(['paid', 'waiting', 'cancel'] * (len(client_objects) // 3))
]

order_objects = [Order.objects.create(**order) for order in orders]


workdays = []
for i in range(10):
    for j, specialist in enumerate(specialist_objects):
        workday = {"workday": f'2024-08-{i+1:02d}', "salon": salon_objects[(i + j) % len(salon_objects)], "specialist": specialist, "start_at": '09:00', "end_at": '18:00'}
        workday_obj = SpecialistWorkDayInSalon.objects.create(**workday)

        if (i + j) % 2 == 0:
            workday_obj.services.add(service_objects[0], service_objects[1])
        else:
            workday_obj.services.add(service_objects[2], service_objects[3])
        workdays.append(workday_obj)


appointments = []
for i, workday in enumerate(workdays):
    services_offered = list(workday.services.all())
    for k in range(2):
        appointment = {
            "status": ['access', 'ended'][(i + k) % 2],
            "date": workday.workday,
            "salon": workday.salon,
            "client": client_objects[(i * 3 + k) % len(client_objects)],
            "specialist": workday.specialist,
            "service": services_offered[k % len(services_offered)],
            "start_at": f'{10 + k}:00',
            "order": order_objects[(i * 3 + k) % len(order_objects)]
        }
        appointments.append(appointment)

    if i < 5:  # Только для первых пяти дней
        appointment = {
            "status": "ended",
            "date": f'2024-07-{20 + i}',  # Даты в прошлом
            "salon": workday.salon,
            "client": client_objects[(i * 3 + 2) % len(client_objects)],
            "specialist": workday.specialist,
            "service": services_offered[2 % len(services_offered)],
            "start_at": '14:00',
            "order": order_objects[(i * 3 + 2) % len(order_objects)]
        }
        appointments.append(appointment)

# Добавление нескольких отменённых заказов с прошлыми датами
past_appointments = [
    {
        "status": "cancel",
        "date": "2024-07-20",
        "salon": salon_objects[0],
        "client": client_objects[0],
        "specialist": specialist_objects[0],
        "service": service_objects[0],
        "start_at": "10:00",
        "order": order_objects[0]
    },
    {
        "status": "cancel",
        "date": "2024-07-21",
        "salon": salon_objects[1],
        "client": client_objects[1],
        "specialist": specialist_objects[1],
        "service": service_objects[1],
        "start_at": "11:00",
        "order": order_objects[1]
    }
]

appointments.extend(past_appointments)

for appointment in appointments:
    Appointment.objects.create(**appointment)
