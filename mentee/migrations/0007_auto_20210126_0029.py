# Generated by Django 2.2 on 2021-01-26 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentee', '0006_mentor_bank_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skills_career',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]