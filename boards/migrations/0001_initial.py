# Generated by Django 4.2 on 2023-06-28 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, unique=True)),
                ('cover', models.ImageField(default='boards/default.png', upload_to='boards')),
                ('is_private', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=250)),
            ],
        ),
    ]