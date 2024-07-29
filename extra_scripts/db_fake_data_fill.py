# import random
# import uuid
# from faker import Faker
from datacenter.models import Client, Salon, Service, Specialist, Order, SpecialistWorkDayInSalon, Appointment


# # # ! запуск через PowerShell команда - >>> exec(open("db_fake_data_fill.py", encoding="utf-8").read())


# clients = [
#     {"id_tg": 224, "full_name": "Иван", "phone_number": "+79699998121"},
#     {"id_tg": 225, "full_name": "Мария", "phone_number": "+79686758122"},
#     {"id_tg": 226, "full_name": "Христина", "phone_number": "+79622228123"},
#     {"id_tg": 227, "full_name": "Кристина", "phone_number": "+79611118123"},
#     {"id_tg": 228, "full_name": "Егор", "phone_number": "+79676448123"},
#     {"id_tg": 229, "full_name": "Виталия", "phone_number": "+79612348123"},
#     {"id_tg": 230, "full_name": "Виталий", "phone_number": "+79601588123"},
#     {"id_tg": 231, "full_name": "Александр", "phone_number": "+79665968123"},
#     {"id_tg": 232, "full_name": "Дарья", "phone_number": "+79634567123"},
#     {"id_tg": 233, "full_name": "Светлана", "phone_number": "+79687998123"},
#     {"id_tg": 234, "full_name": "Максим", "phone_number": "+79631238123"},
#     {"id_tg": 235, "full_name": "Анна", "phone_number": "+79665828123"},
#     {"id_tg": 236, "full_name": "Олег", "phone_number": "+79624356123"},
#     {"id_tg": 237, "full_name": "Татьяна", "phone_number": "+79657899123"},
#     {"id_tg": 238, "full_name": "Юлия", "phone_number": "+79681234123"},
#     {"id_tg": 239, "full_name": "Дмитрий", "phone_number": "+79667587123"},
#     {"id_tg": 240, "full_name": "Алина", "phone_number": "+79609877123"},
#     {"id_tg": 241, "full_name": "Николай", "phone_number": "+79621432123"},
#     {"id_tg": 242, "full_name": "Виктория", "phone_number": "+79632678123"},
#     {"id_tg": 243, "full_name": "Константин", "phone_number": "+79643218123"}
# ]

# client_objects = [Client.objects.create(**client) for client in clients]


# salons = [
#     {"title": "Tip-Top", "address": "г. Москва ул. Красноармейская, д. 1"},
#     {"title": "Glamour", "address": "г. Москва ул. Ленина, д. 5"},
#     {"title": "Beauty Plus", "address": "г. Москва ул. Тверская, д. 10"}
# ]

# salon_objects = [Salon.objects.create(**salon) for salon in salons]


# services = [
#     {"title": "Окрашивание", "price": 4500.0, "duration": 180},
#     {"title": "Маникюр", "price": 1500.0, "duration": 60},
#     {"title": "Стрижка", "price": 2000.0, "duration": 90},
#     {"title": "Педикюр", "price": 2500.0, "duration": 90}
# ]

# service_objects = [Service.objects.create(**service) for service in services]


# specialists = [
#     {"full_name": "Иван Иван Иваныч"},
#     {"full_name": "Петр Петрович"},
#     {"full_name": "Мария Ивановна"},
#     {"full_name": "Александр Ракшин"},
#     {"full_name": "Ксения Кузнецова"},
#     {"full_name": "Мария Петровна"},
#     {"full_name": "Сергей Сергеевич"}
# ]

# specialist_objects = [Specialist.objects.create(**specialist) for specialist in specialists]


# orders = [
#     {"client": client_objects[i], "status": status, "receipt": f'https://www.example.com/receipt{i}'}
#     for i, status in enumerate(['paid', 'waiting', 'cancel'] * (len(client_objects) // 3))
# ]

# order_objects = [Order.objects.create(**order) for order in orders]


# workdays = []
# for i in range(10):
#     for j, specialist in enumerate(specialist_objects):
#         workday = {"workday": f'2024-08-{i+1:02d}', "salon": salon_objects[(i + j) % len(salon_objects)], "specialist": specialist, "start_at": '09:00', "end_at": '18:00'}
#         workday_obj = SpecialistWorkDayInSalon.objects.create(**workday)

#         if (i + j) % 2 == 0:
#             workday_obj.services.add(service_objects[0], service_objects[1])
#         else:
#             workday_obj.services.add(service_objects[2], service_objects[3])
#         workdays.append(workday_obj)


# appointments = []
# for i, workday in enumerate(workdays):
#     services_offered = list(workday.services.all())
#     for k in range(2):
#         appointment = {
#             "status": ['access', 'ended'][1],
#             "date": workday.workday,
#             "salon": workday.salon,
#             "client": client_objects[(i * 3 + k) % len(client_objects)],
#             "specialist": workday.specialist,
#             "service": services_offered[k % len(services_offered)],
#             "start_at": f'{10 + k}:00',
#             "order": order_objects[(i * 3 + k) % len(order_objects)]
#         }
#         appointments.append(appointment)

#     if i < 5:  # Только для первых пяти дней
#         appointment = {
#             "status": "ended",
#             "date": f'2024-07-{20 + i}',  # Даты в прошлом
#             "salon": workday.salon,
#             "client": client_objects[(i * 3 + 2) % len(client_objects)],
#             "specialist": workday.specialist,
#             "service": services_offered[2 % len(services_offered)],
#             "start_at": '14:00',
#             "order": order_objects[(i * 3 + 2) % len(order_objects)]
#         }
#         appointments.append(appointment)

# # Добавление нескольких отменённых заказов с прошлыми датами
# past_appointments = [
#     {
#         "status": "cancel",
#         "date": "2024-07-20",
#         "salon": salon_objects[0],
#         "client": client_objects[0],
#         "specialist": specialist_objects[0],
#         "service": service_objects[0],
#         "start_at": "10:00",
#         "order": order_objects[0]
#     },
#     {
#         "status": "cancel",
#         "date": "2024-07-21",
#         "salon": salon_objects[1],
#         "client": client_objects[1],
#         "specialist": specialist_objects[1],
#         "service": service_objects[1],
#         "start_at": "11:00",
#         "order": order_objects[1]
#     }
# ]

# appointments.extend(past_appointments)

# for appointment in appointments:
#     Appointment.objects.create(**appointment)



# Создание клиентов
Client.objects.create(id_tg=100, full_name='Ричард', phone_number='+79004217012')
Client.objects.create(id_tg=101, full_name='Егор', phone_number='+79004216012')
Client.objects.create(id_tg=102, full_name='Александр', phone_number='+79004215012')
Client.objects.create(id_tg=103, full_name='Николай', phone_number='+79004214012')
Client.objects.create(id_tg=104, full_name='Виктория', phone_number='+79004213012')
Client.objects.create(id_tg=105, full_name='Елизавета', phone_number='+79004212012')
Client.objects.create(id_tg=106, full_name='Христина', phone_number='+79004211012')

client1 = Client.objects.get(id_tg=100)
client2 = Client.objects.get(id_tg=101)
client3 = Client.objects.get(id_tg=102)
client4 = Client.objects.get(id_tg=103)
client5 = Client.objects.get(id_tg=104)
client6 = Client.objects.get(id_tg=105)
client7 = Client.objects.get(id_tg=106)

# Создание салонов
Salon.objects.create(title="Tip-Top", address="г. Москва ул. Красноармейская, д. 2")
Salon.objects.create(title="Glamour", address="г. Москва ул. Красноармейская, д. 1")
Salon.objects.create(title="Beauty Plus", address="г. Москва ул. Красноармейская, д. 3")

salon1 = Salon.objects.get(title="Tip-Top")
salon2 = Salon.objects.get(title="Glamour")
salon3 = Salon.objects.get(title="Beauty Plus")

# Создание услуг
Service.objects.create(title="Окрашивание", price=4500.0, duration=180)
Service.objects.create(title="Маникюр", price=1500.0, duration=60)
Service.objects.create(title="Стрижка", price=2000.0, duration=90)
Service.objects.create(title="Педикюр", price=2500.0, duration=90)
Service.objects.create(title="Депиляция", price=15000.0, duration=180)
Service.objects.create(title="Стрижка ножницами", price=2500.0, duration=120)
Service.objects.create(title="Массаж лица", price=1200.0, duration=30)

service_1 = Service.objects.get(title="Окрашивание")
service_2 = Service.objects.get(title="Маникюр")
service_3 = Service.objects.get(title="Стрижка")
service_4 = Service.objects.get(title="Педикюр")
service_5 = Service.objects.get(title="Депиляция")
service_6 = Service.objects.get(title="Стрижка ножницами")
service_7 = Service.objects.get(title="Массаж лица")

# Создание специалистов
Specialist.objects.create(full_name="Иван Иванов")
Specialist.objects.create(full_name="Петр Петров")
Specialist.objects.create(full_name="Мария Смирнова")
Specialist.objects.create(full_name="Александр Кузнецов")
Specialist.objects.create(full_name="Ксения Лебедева")
Specialist.objects.create(full_name="Сергей Николаев")

specialist1 = Specialist.objects.get(full_name="Иван Иванов")
specialist2 = Specialist.objects.get(full_name="Петр Петров")
specialist3 = Specialist.objects.get(full_name="Мария Смирнова")
specialist4 = Specialist.objects.get(full_name="Александр Кузнецов")
specialist5 = Specialist.objects.get(full_name="Ксения Лебедева")
specialist6 = Specialist.objects.get(full_name="Сергей Николаев")

# Создание заказов
Order.objects.create(client=client1, status='paid', receipt='https://google.com')
Order.objects.create(client=client2, status='paid', receipt='https://google.com')
Order.objects.create(client=client3, status='paid', receipt='https://google.com')

order1 = Order.objects.get(client=client1)
order2 = Order.objects.get(client=client2)
order3 = Order.objects.get(client=client3)

# Создание рабочих днейг
workday1 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-28",
    salon=salon1,
    specialist=specialist1,
    start_at='08:00',
    end_at='18:00'
)
workday1.services.add(service_1, service_2)

workday2 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-30",
    salon=salon2,
    specialist=specialist1,
    start_at='07:00',
    end_at='17:00'
)
workday2.services.add(service_2)

workday3 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-03",
    salon=salon3,
    specialist=specialist1,
    start_at='08:00',
    end_at='18:00'
)
workday3.services.add(service_2, service_6, service_7)

workday4 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-05",
    salon=salon1,
    specialist=specialist2,
    start_at='08:00',
    end_at='18:00'
)
workday4.services.add(service_1, service_6, service_2)

workday5 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-12",
    salon=salon2,
    specialist=specialist2,
    start_at='07:00',
    end_at='17:00'
)
workday5.services.add(service_2, service_3, service_7)

workday6 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-01",
    salon=salon3,
    specialist=specialist2,
    start_at='08:00',
    end_at='18:00'
)
workday6.services.add(service_2, service_5, service_7)

workday7 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-02",
    salon=salon1,
    specialist=specialist3,
    start_at='08:00',
    end_at='18:00'
)
workday7.services.add(service_1, service_2)

workday8 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-10",
    salon=salon2,
    specialist=specialist3,
    start_at='07:00',
    end_at='17:00'
)
workday8.services.add(service_2, service_4, service_7)

workday9 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-29",
    salon=salon3,
    specialist=specialist3,
    start_at='08:00',
    end_at='18:00'
)
workday9.services.add(service_4, service_5, service_7)

workday10 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-08-02",
    salon=salon1,
    specialist=specialist4,
    start_at='08:00',
    end_at='18:00'
)
workday10.services.add(service_6, service_1)

workday11 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-10-28",
    salon=salon2,
    specialist=specialist4,
    start_at='07:00',
    end_at='17:00'
)
workday11.services.add(service_2, service_3, service_7, service_5)

workday12 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-11-29",
    salon=salon3,
    specialist=specialist4,
    start_at='08:00',
    end_at='18:00'
)
workday12.services.add(service_4)

workday13 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-28",
    salon=salon1,
    specialist=specialist5,
    start_at='08:00',
    end_at='18:00'
)
workday13.services.add(service_1, service_2)

workday14 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-30",
    salon=salon2,
    specialist=specialist5,
    start_at='07:00',
    end_at='17:00'
)
workday14.services.add(service_2, service_6)

workday15 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-31",
    salon=salon3,
    specialist=specialist5,
    start_at='08:00',
    end_at='18:00'
)
workday15.services.add(service_2, service_6, service_7)

workday16 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-28",
    salon=salon1,
    specialist=specialist6,
    start_at='08:00',
    end_at='18:00'
)
workday16.services.add(service_1, service_2)

workday17 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-30",
    salon=salon2,
    specialist=specialist6,
    start_at='07:00',
    end_at='17:00'
)
workday17.services.add(service_2)

workday18 = SpecialistWorkDayInSalon.objects.create(
    workday="2024-07-31",
    salon=salon3,
    specialist=specialist6,
    start_at='08:00',
    end_at='18:00'
)
workday18.services.add(service_2, service_6, service_7)

# записи
Appointment.objects.create(status='access', date='2024-07-30', salon=salon3, client=client1, specialist=specialist6, service=service_1, start_at='10:00', order=order1)
Appointment.objects.create(status='access', date='2024-07-30', salon=salon3, client=client2, specialist=specialist6, service=service_2, start_at='12:00', order=order2)
Appointment.objects.create(status='access', date='2024-07-30', salon=salon3, client=client3, specialist=specialist6, service=service_3, start_at='14:00', order=order3)
Appointment.objects.create(status='ended', date='2024-07-25', salon=salon3, client=client4, specialist=specialist5, service=service_3, start_at='16:00')
Appointment.objects.create(status='ended', date='2024-07-25', salon=salon3, client=client5, specialist=specialist5, service=service_4, start_at='18:00')
Appointment.objects.create(status='discard', date='2024-08-01', salon=salon1, client=client6, specialist=specialist4, service=service_1, start_at='10:00')
Appointment.objects.create(status='discard', date='2024-08-01', salon=salon1, client=client7, specialist=specialist4, service=service_2, start_at='12:00')
