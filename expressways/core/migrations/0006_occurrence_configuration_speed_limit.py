# Generated by Django 2.1.3 on 2019-04-04 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_sub_occurrence_configuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrenceconfiguration',
            name='speed_limit',
            field=models.PositiveIntegerField(choices=[(70, '70'), (60, '60'), (50, '50'), (40, '40')], default=70),
        ),
        migrations.AlterField(
            model_name='occurrenceconfiguration',
            name='flow',
            field=models.PositiveIntegerField(choices=[(1750, 'High'), (1250, 'Medium High'), (750, 'Medium Low'), (300, 'Low')], default=300, verbose_name='flow rate'),
        ),
        migrations.AlterField(
            model_name='occurrenceconfiguration',
            name='lane_closures',
            field=models.CharField(choices=[('II', 'II'), ('IX', 'IX'), ('XI', 'XI'), ('XX', 'XX')], default='II', max_length=2, verbose_name='impact'),
        ),
    ]
