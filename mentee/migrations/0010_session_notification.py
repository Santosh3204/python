# Generated by Django 2.2 on 2021-01-31 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentee', '0009_menteedetails_school_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='session_notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_id', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]
