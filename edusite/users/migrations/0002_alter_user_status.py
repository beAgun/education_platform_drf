# Generated by Django 4.2.1 on 2024-03-02 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.BooleanField(choices=[(True, 'Преподаватель'), (False, 'Студент')], default=0, verbose_name='Статус'),
        ),
    ]
