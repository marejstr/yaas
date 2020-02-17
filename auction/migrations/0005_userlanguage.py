# Generated by Django 2.2.5 on 2019-11-07 23:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('auction', '0004_usercurrency'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLanguage',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('language', models.CharField(default='en', max_length=3)),
            ],
        ),
    ]
