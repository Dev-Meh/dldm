from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'SYSTEM_ADMIN', 'System Admin'
        STOCK_MANAGER = 'STOCK_MANAGER', 'Stock Manager'
        SALES_MANAGER = 'SALES_MANAGER', 'Sales Manager'
        COMPANY_MANAGER = 'COMPANY_MANAGER', 'Company Manager'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SYSTEM_ADMIN
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+255999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=15,
        blank=True,
        null=True
    )
