# Generated by Django 4.0.4 on 2022-12-19 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='filter_query',
            fields=[
                ('mq_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('description', models.CharField(blank=True, max_length=4096, null=True)),
                ('selected', models.CharField(blank=True, max_length=4096, null=True)),
                ('conditions', models.CharField(blank=True, max_length=4096, null=True)),
                ('tables', models.CharField(blank=True, max_length=4096, null=True)),
                ('public', models.IntegerField(blank=True, null=True)),
                ('active', models.IntegerField(blank=True, null=True)),
                ('topic_name', models.CharField(blank=True, max_length=256, null=True)),
                ('real_sql', models.CharField(blank=True, max_length=4096, null=True)),
                ('date_created', models.DateTimeField(auto_now=True, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(blank=True, db_column='user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'myqueries',
                'managed': True,
            },
        ),
    ]