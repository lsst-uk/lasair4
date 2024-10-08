# Generated by Django 4.0.4 on 2022-05-25 15:54

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
            name='Watchlists',
            fields=[
                ('wl_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('description', models.CharField(blank=True, max_length=4096, null=True)),
                ('active', models.IntegerField(blank=True, null=True)),
                ('public', models.IntegerField(blank=True, null=True)),
                ('radius', models.FloatField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(blank=True, db_column='user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'watchlists',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='WatchlistCones',
            fields=[
                ('cone_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('ra', models.FloatField(blank=True, null=True)),
                ('decl', models.FloatField(blank=True, null=True)),
                ('radius', models.FloatField(blank=True, null=True)),
                ('wl', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='lasair.watchlists')),
            ],
            options={
                'db_table': 'watchlist_cones',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Myqueries',
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
                ('user', models.ForeignKey(blank=True, db_column='user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'myqueries',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Areas',
            fields=[
                ('ar_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('description', models.CharField(blank=True, max_length=4096, null=True)),
                ('moc', models.TextField(blank=True, null=True)),
                ('mocimage', models.TextField(blank=True, null=True)),
                ('active', models.IntegerField(blank=True, null=True)),
                ('public', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(blank=True, db_column='user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'areas',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Annotators',
            fields=[
                ('topic', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('password', models.CharField(blank=True, max_length=32, null=True)),
                ('url', models.CharField(blank=True, max_length=1024, null=True)),
                ('active', models.IntegerField(blank=True, null=True)),
                ('public', models.IntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, db_column='user', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'annotators',
                'managed': True,
            },
        ),
    ]
