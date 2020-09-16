# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-03-13 06:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0003_requesteditem_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requesteditem',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(13, 'Shareable'), (14, 'Returnable'), (15, 'Permanent')]),
        ),
    ]