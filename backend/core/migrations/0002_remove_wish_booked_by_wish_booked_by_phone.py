# Generated by Django 4.1.10 on 2024-12-12 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wish',
            name='booked_by',
        ),
        migrations.AddField(
            model_name='wish',
            name='booked_by_phone',
            field=models.CharField(default=0, max_length=17),
        ),
    ]
