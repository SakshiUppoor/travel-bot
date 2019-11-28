# Generated by Django 2.2.5 on 2019-11-26 16:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0002_auto_20191126_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='from_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='to_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
