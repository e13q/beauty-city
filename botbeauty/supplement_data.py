import random
import uuid
from faker import Faker
from mybot.models import Client, Salon, Service, Specialist, Order, SpecialistWorkDayInSalon, Appointment


# ! pip install faker
# ! запуск через PowerShell команда - >>> exec(open("supplement_data.py", encoding="utf-8").read())


fake = Faker('ru_RU')


def generate_phone_number():
    return f"+7{fake.msisdn()[1:]}"


def generate_url():
    return f"https://example.com/receipt/{uuid.uuid4()}"


def generate_date():
    return f"2024-08-{random.randint(1, 31):02d}"


# Создание клиентов
clients = []
for _ in range(100):
    clients.append(Client.objects.create(
        id_tg=random.randint(1, 10000),
        full_name=fake.name(),
        phone_number=generate_phone_number()
    ))


# Создание салонов
salons = []
for _ in range(10):
    salons.append(Salon.objects.create(
        title=fake.company(),
        address=fake.address()
    ))

# Создание услуг
services = []
services_list = [("Окрашивание", 4500.0, 180),
                 ("Маникюр", 1500.0, 60),
                 ("Стрижка", 2000.0, 90),
                 ("Педикюр", 2500.0, 90)]
for title, price, duration in services_list:
    for _ in range(10):
        services.append(Service.objects.create(
            title=f"{title} {fake.word()}",
            price=price,
            duration=duration
        ))

# Создание специалистов
specialists = []
for _ in range(20):
    specialists.append(Specialist.objects.create(
        full_name=fake.name()
    ))

# Создание заказов
orders = []
for _ in range(300):
    client = random.choice(clients)
    orders.append(Order.objects.create(
        client=client,
        status=random.choice(['paid', 'waiting', 'cancel']),
        receipt=generate_url()
    ))

# Создание рабочих дней специалистов в салонах
workdays = []
for _ in range(200):
    salon = random.choice(salons)
    specialist = random.choice(specialists)
    workday = generate_date()
    start_at = f"{random.randint(8, 10)}:00"
    end_at = f"{random.randint(17, 19)}:00"
    workday_obj = SpecialistWorkDayInSalon.objects.create(
        workday=workday,
        salon=salon,
        specialist=specialist,
        start_at=start_at,
        end_at=end_at
    )
    workday_obj.services.set(random.sample(services, k=random.randint(1, 4)))
    workdays.append(workday_obj)

# Создание записей о заказах услуг
appointments = []
for _ in range(500):
    status = random.choice(['access', 'ended', 'discard'])
    date = generate_date()
    salon = random.choice(salons)
    client = random.choice(clients)
    specialist = random.choice(specialists)
    service = random.choice(services)
    start_at = f"{random.randint(8, 16)}:00"
    order = random.choice(orders)
    appointments.append(Appointment.objects.create(
        status=status,
        date=date,
        salon=salon,
        client=client,
        specialist=specialist,
        service=service,
        start_at=start_at,
        order=order
    ))
