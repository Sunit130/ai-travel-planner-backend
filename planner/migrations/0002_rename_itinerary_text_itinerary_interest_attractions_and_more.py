# Generated by Django 5.1.6 on 2025-02-07 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itinerary',
            old_name='itinerary_text',
            new_name='interest_attractions',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='vote_type',
        ),
        migrations.AddField(
            model_name='itinerary',
            name='itinerary_plan',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='overview_introduction',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itinerary',
            name='overview_time_to_visit',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='itinerary',
            name='top_attractions',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vote',
            name='is_upvote',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='itinerary',
            name='budget',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
