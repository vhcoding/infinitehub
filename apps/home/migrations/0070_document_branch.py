# Generated by Django 4.2.11 on 2024-04-22 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0069_branch_bill_payer'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='branch',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to='home.branch'),
        ),
    ]