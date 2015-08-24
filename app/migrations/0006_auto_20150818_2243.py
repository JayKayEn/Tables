# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20150817_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='most_recent_post',
            field=models.CharField(null=True, max_length=10),
        ),
    ]
