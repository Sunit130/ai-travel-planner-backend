# Generated by Django 5.1.6 on 2025-02-12 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0004_alter_itinerary_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='destination_slug',
            field=models.SlugField(blank=True, max_length=100, unique=True),
        ),
    ]
