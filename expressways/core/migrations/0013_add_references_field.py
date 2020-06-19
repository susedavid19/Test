# Generated by Django 2.2.13 on 2020-06-17 19:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_add_incidents_cleared'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrenceconfiguration',
            name='references',
            field=models.TextField(default='', help_text='Provide references to data sources or a detailed explanation of any assumptions used e.g. calculations to determine frequencies or durations.'),
        ),
        migrations.AlterField(
            model_name='effectintervention',
            name='duration_change',
            field=models.IntegerField(help_text='% change in duration', validators=[django.core.validators.MinValueValidator(-100)], verbose_name='Duration change (%)'),
        ),
        migrations.AlterField(
            model_name='effectintervention',
            name='frequency_change',
            field=models.IntegerField(help_text='% change in frequency', validators=[django.core.validators.MinValueValidator(-100)], verbose_name='Frequency change (%)'),
        ),
        migrations.AlterField(
            model_name='occurrenceconfiguration',
            name='frequency',
            field=models.PositiveIntegerField(help_text='Define the frequency of the occurrence (average per mile per year)\u200b'),
        ),
    ]
