# Generated by Django 2.2.13 on 2020-11-08 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonds', '0002_bond_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='bond',
            name='legal_name',
            field=models.CharField(max_length=255),
            preserve_default=False,
        ),
    ]