# Generated by Django 4.2.5 on 2023-09-15 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_profile_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='first_login',
            field=models.BooleanField(default=True),
        ),
    ]
