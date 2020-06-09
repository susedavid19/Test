# Generated by Django 2.2.13 on 2020-06-09 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_add_objective_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrenceconfiguration',
            name='incidents_cleared',
            field=models.BooleanField(default=False, help_text='If ticked, incidents occurring as a result of this Operational Occurrence will be included in the ‘Incidents Cleared’ calculation'),
        ),
    ]
