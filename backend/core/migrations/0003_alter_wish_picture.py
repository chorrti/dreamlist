# Generated by Django 4.1.10 on 2024-12-12 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_wish_booked_by_wish_booked_by_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wish',
            name='picture',
            field=models.ImageField(default='blank_profile_picture.png', upload_to='wish_images'),
        ),
    ]