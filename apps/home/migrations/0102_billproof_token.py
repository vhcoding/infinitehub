# Generated by Django 4.2.14 on 2024-08-06 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0101_alter_bill_payer_alter_billproof_bill'),
    ]

    operations = [
        migrations.AddField(
            model_name='billproof',
            name='token',
            field=models.CharField(default='', max_length=64),
        ),
    ]
