# Generated by Django 4.2 on 2023-06-09 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_forgotpassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forgotpassword',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forgot_pass', to=settings.AUTH_USER_MODEL),
        ),
    ]
