# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-03-13 05:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('trashed', models.BooleanField(db_index=True, default=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(10, 'Pending'), (11, 'Acknowledged'), (12, 'Returned')], default=10)),
                ('approved_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items_approved_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('trashed', models.BooleanField(db_index=True, default=False)),
                ('quantity', models.IntegerField(default=1)),
                ('type', models.PositiveSmallIntegerField(choices=[(13, 'Shareable'), (14, 'Returnable'), (15, 'Permanent')], default=14)),
                ('is_assigned', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('trashed', models.BooleanField(db_index=True, default=False)),
                ('attribute_name', models.CharField(max_length=100)),
                ('attribute_value', models.CharField(max_length=100)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='item.Item')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('trashed', models.BooleanField(db_index=True, default=False)),
                ('item_name', models.CharField(max_length=100, unique=True)),
                ('is_accessory', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_groups', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_groups', to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RequestedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('trashed', models.BooleanField(db_index=True, default=False)),
                ('status', models.PositiveSmallIntegerField(choices=[(7, 'Pending'), (8, 'Approved'), (9, 'Cancelled')], default=7)),
                ('quantity', models.IntegerField(default=1)),
                ('item_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='item.ItemGroup')),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL)),
                ('requested_to', models.ManyToManyField(related_name='requests_to_approve', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='item',
            name='item_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='item.ItemGroup'),
        ),
        migrations.AddField(
            model_name='approveditem',
            name='approved_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approved_items', to='item.Item'),
        ),
        migrations.AddField(
            model_name='approveditem',
            name='approved_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items_approved_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='approveditem',
            name='request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='approved_item', to='item.RequestedItem'),
        ),
    ]