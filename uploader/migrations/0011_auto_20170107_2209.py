# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-07 22:09
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0010_uploadedfile_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 7, 22, 9, 17, 689365, tzinfo=utc)),
        ),
    ]
