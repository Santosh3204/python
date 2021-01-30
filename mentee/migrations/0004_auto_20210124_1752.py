# Generated by Django 2.2 on 2021-01-24 17:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mentee', '0003_auto_20210124_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='webinar',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='webinar',
            name='status',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='webinar',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]