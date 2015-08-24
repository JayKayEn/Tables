# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('value', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Followees',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('profile', models.CharField(null=True, unique=True, max_length=30)),
                ('user_id', models.CharField(serialize=False, max_length=20, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('profile_picture_url', models.URLField(null=True)),
                ('full_name', models.CharField(null=True, blank=True, max_length=20)),
                ('most_recent_post', models.DateTimeField(default=django.utils.timezone.now)),
                ('needs_review', models.BooleanField(default=False)),
                ('new_post_count', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='followees',
            name='people',
            field=models.ManyToManyField(to='app.Person'),
        ),
        migrations.AddField(
            model_name='followees',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
