# Generated by Django 2.1.3 on 2018-11-15 13:42

from django.db import migrations, models
import django.db.models.deletion

def add_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    Group = apps.get_model('auth', 'Group')
    group = Group.objects.get(name='operators')

    Occurrence = apps.get_model('core', 'Occurrence')
    content_type = ContentType.objects.get_for_model(Occurrence)
    for permission in Permission.objects.filter(content_type=content_type):
        if permission.codename.startswith(('add_', 'view_')):
            group.permissions.add(permission)

    SubOccurrence = apps.get_model('core', 'SubOccurrence')
    content_type = ContentType.objects.get_for_model(SubOccurrence)
    for permission in Permission.objects.filter(content_type=content_type):
        if permission.codename.startswith(('add_', 'view_')):
            group.permissions.add(permission)

    group.save()

def remove_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    Group = apps.get_model('auth', 'Group')
    group = Group.objects.get(name='operators')

    Occurrence = apps.get_model('core', 'Occurrence')
    content_type = ContentType.objects.get_for_model(Occurrence)
    for permission in Permission.objects.filter(content_type=content_type):
        group.permissions.remove(permission)

    SubOccurrence = apps.get_model('core', 'SubOccurrence')
    content_type = ContentType.objects.get_for_model(SubOccurrence)
    for permission in Permission.objects.filter(content_type=content_type):
        group.permissions.remove(permission)

    group.save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_create_user_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('archived', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SubOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('archived', models.BooleanField(default=False)),
                ('occurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_occurrences', to='core.Occurrence')),
            ],
        ),
        migrations.RunPython(add_permissions, remove_permissions),
    ]
