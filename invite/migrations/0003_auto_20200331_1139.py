# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-03-31 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0002_auto_20200307_0349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invite',
            name='key',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]