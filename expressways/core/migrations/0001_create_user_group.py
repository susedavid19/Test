# Generated by Django 2.1.3 on 2018-11-02 17:12

from django.db import migrations

NAME = 'operators'

def create_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=NAME)

def remove_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
