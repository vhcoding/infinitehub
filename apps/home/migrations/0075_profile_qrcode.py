# Generated by Django 4.2.11 on 2024-05-27 12:49

import apps.home.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0074_profile_facebook_profile_instagram_profile_linkedin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='qrcode',
            field=models.ImageField(default='placeholder.webp', storage=apps.home.storage_backends.PublicMediaStorage(), upload_to='qrcodes/members/'),
        ),
    ]
