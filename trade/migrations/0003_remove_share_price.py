# Generated by Django 3.2.4 on 2021-07-01 15:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0002_auto_20210701_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='share',
            name='price',
        ),
    ]