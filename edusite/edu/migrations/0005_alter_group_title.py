# Generated by Django 4.2.1 on 2024-03-02 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0004_enrollment_date_product_rule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(default='group', max_length=255, verbose_name='Название'),
        ),
    ]