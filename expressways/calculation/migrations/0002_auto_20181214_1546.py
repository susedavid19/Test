# Generated by Django 2.1.3 on 2018-12-14 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculationresult',
            name='objective_1',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='calculationresult',
            name='objective_2',
            field=models.FloatField(),
        ),
    ]
