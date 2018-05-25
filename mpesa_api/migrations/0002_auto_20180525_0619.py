# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mpesa_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlinecheckout',
            name='order_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='onlinecheckoutresponse',
            name='order_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
