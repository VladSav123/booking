from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Перевірка, чи передано електронну пошту
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Створення суперкористувача зі значеннями за замовчуванням
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # Модель користувача зі зв'язком з CustomUserManager
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    register_date = models.DateField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email   
        
        
class Ticket_plane(models.Model):
    # Модель для збереження інформації про квитки на літак
    departure = models.CharField(max_length=100)  # Місто відправлення
    destination = models.CharField(max_length=100)  # Місто призначення
    departure_date = models.DateField()  # Дата відправлення
    departure_time = models.DateTimeField()
    destination_date = models.DateTimeField()  # Дата відправлення
    plane_name = models.CharField(max_length=100)  # Тип літака (наприклад, Boeing 737)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ціна квитка
    available_seats = models.IntegerField()  # Кількість доступних місць

    def is_ticket_active(self):
        # Перевірка, чи квиток активний (чи є доступні місця)
        return self.available_seats > 0
        
        
class Subscribed_users(models.Model):
    # Модель для збереження даних підписаних користувачів
    email = models.CharField(max_length = 100)
    subscribed_from = models.DateField(default=timezone.now)
    
class Promocodes(models.Model):
    # Модель для збереження промокодів
    promocode = models.CharField(max_length = 100)
    expire = models.DateField(default=timezone.now)
    available = models.BooleanField(default=True)