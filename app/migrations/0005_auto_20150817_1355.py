# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150817_0040'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['username']},
        ),
    ]
