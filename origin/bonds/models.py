from django.contrib.auth.models import User
from django.core import validators
from django.db import models


class Bond(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isin = models.CharField(max_length=12, validators=[validators.RegexValidator(r'^[a-zA-Z0-9]*$')])
    size = models.IntegerField()
    currency = models.CharField(max_length=3, validators=[validators.RegexValidator(r'^[A-Z]{3}$')])
    maturity = models.DateField()
    lei = models.CharField(max_length=20, validators=[validators.RegexValidator(r'^[A-Z0-9]{20}$')])
    legal_name = models.CharField(max_length=255)
