# Generated by Django 2.1.3 on 2019-06-11 17:09

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0006_calculation_with_component_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculationresult',
            name='freq_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None),
        ),
    ]
