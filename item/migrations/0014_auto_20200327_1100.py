# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-03-27 11:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0013_auto_20200327_1008'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='approveditem',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='itemattribute',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='itemgroup',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='itemhistory',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='requesteditem',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='itemhistory',
            name='approved_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='item.ApprovedItem'),
        ),
    ]
