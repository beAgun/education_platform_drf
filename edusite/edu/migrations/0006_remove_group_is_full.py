# Generated by Django 4.2.1 on 2024-03-02 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0005_alter_group_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='is_full',
        ),
    ]