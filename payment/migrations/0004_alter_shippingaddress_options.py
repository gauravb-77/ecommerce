# Generated by Django 5.1 on 2024-09-10 05:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_alter_shippingaddress_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shippingaddress',
            options={'verbose_name_plural': 'Shipping '},
        ),
    ]
