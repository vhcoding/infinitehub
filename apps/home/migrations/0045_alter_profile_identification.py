# Generated by Django 4.2.9 on 2024-01-29 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0044_remove_profile_registration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='identification',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]
