# Generated by Django 3.0.8 on 2020-08-21 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hms', '0003_reservation_customername'),
    ]

    operations = [
        migrations.AddField(
            model_name='waitlist',
            name='customerName',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='waitlist',
            name='date',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='waitlist',
            name='status',
            field=models.CharField(choices=[('0', 'pending'), ('1', 'confirmed')], default='0', max_length=100),
        ),
    ]
