# Generated by Django 4.2.5 on 2023-11-29 13:35

import apps.home.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_uploadeddocument'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadeddocument',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=apps.home.models.custom_upload_path_documents),
        ),
    ]
