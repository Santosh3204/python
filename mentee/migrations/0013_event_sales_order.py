# Generated by Django 2.2 on 2021-01-31 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mentee', '0012_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='event_sales_order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.IntegerField()),
                ('mentee_id', models.IntegerField()),
                ('payment_id', models.CharField(max_length=100, null=True)),
                ('status', models.SmallIntegerField(default=0)),
                ('user_order_id', models.CharField(max_length=100, null=True)),
                ('mentee_name', models.CharField(blank=True, max_length=100, null=True)),
                ('mentee_phonenumber', models.CharField(max_length=15)),
                ('mentee_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('event_price', models.PositiveIntegerField(null=True)),
                ('coupon_used', models.BooleanField(default=False)),
                ('coupon_amount', models.FloatField(null=True)),
                ('coupon_code', models.CharField(max_length=30, null=True)),
                ('wallet_used', models.BooleanField(default=False)),
                ('wallet_amount', models.IntegerField(null=True)),
                ('final_price', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status_updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
