# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-06 12:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('junto_api', '0009_auto_20171006_1439'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
    ]
