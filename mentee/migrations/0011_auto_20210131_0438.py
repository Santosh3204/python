# Generated by Django 2.2 on 2021-01-31 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentee', '0010_session_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session_notification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
