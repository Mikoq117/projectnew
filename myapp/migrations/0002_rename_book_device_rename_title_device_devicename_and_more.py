# Generated by Django 5.1.2 on 2024-10-24 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Book',
            new_name='Device',
        ),
        migrations.RenameField(
            model_name='device',
            old_name='title',
            new_name='devicename',
        ),
        migrations.RenameField(
            model_name='device',
            old_name='author',
            new_name='user',
        ),
    ]
