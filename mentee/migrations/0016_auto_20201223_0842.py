# Generated by Django 2.2 on 2020-12-23 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentee', '0015_auto_20201223_0836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callhistory',
            name='reason',
            field=models.IntegerField(null=True),
        ),
    ]