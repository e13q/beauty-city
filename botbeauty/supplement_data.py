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
    {"id_tg": 235, "full_name": "Анна", "phone_number": "+79665828123"}
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
    {"client": client_objects[0], "status": 'paid', "receipt": 'https://www.google.com'},
    {"client": client_objects[1], "status": 'waiting', "receipt": 'https://www.yandex.ru'},
    {"client": client_objects[2], "status": 'cancel', "receipt": 'https://www.mail.ru'},
    {"client": client_objects[3], "status": 'paid', "receipt": 'https://www.example.com'},
    {"client": client_objects[4], "status": 'waiting', "receipt": 'https://www.example.org'},
    {"client": client_objects[5], "status": 'cancel', "receipt": 'https://www.example.net'}
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
    appointments.extend([
        {"status": 'access', "date": workday.workday, "salon": workday.salon, "client": client_objects[i % len(client_objects)], "specialist": workday.specialist, "service": service_objects[0], "start_at": '09:00', "order": order_objects[i % len(order_objects)]},
        {"status": 'ended', "date": workday.workday, "salon": workday.salon, "client": client_objects[(i + 1) % len(client_objects)], "specialist": workday.specialist, "service": service_objects[1], "start_at": '11:00', "order": order_objects[(i + 1) % len(order_objects)]},
        {"status": 'discard', "date": workday.workday, "salon": workday.salon, "client": client_objects[(i + 2) % len(client_objects)], "specialist": workday.specialist, "service": service_objects[2], "start_at": '13:00', "order": order_objects[(i + 2) % len(order_objects)]},
        {"status": 'access', "date": workday.workday, "salon": workday.salon, "client": client_objects[(i + 3) % len(client_objects)], "specialist": workday.specialist, "service": service_objects[3], "start_at": '15:00', "order": order_objects[(i + 3) % len(order_objects)]},
        {"status": 'ended', "date": workday.workday, "salon": workday.salon, "client": client_objects[(i + 4) % len(client_objects)], "specialist": workday.specialist, "service": service_objects[0], "start_at": '17:00', "order": order_objects[(i + 4) % len(order_objects)]},
        {"status": 'discard', "date": workday.workday, "salon": workday.salon, "client": client_objects[(i + 5) % len(client_objects)], "specialist": workday.specialist, "service": service_objects[1], "start_at": '18:00', "order": order_objects[(i + 5) % len(order_objects)]}
    ])

for appointment in appointments:
    Appointment.objects.create(**appointment)
