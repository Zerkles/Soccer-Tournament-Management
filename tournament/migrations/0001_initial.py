# Generated by Django 4.0.5 on 2022-06-25 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tournament_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tournament_id', models.IntegerField()),
                ('player_a', models.CharField(default=None, max_length=255, null=True)),
                ('player_b', models.CharField(default=None, max_length=255, null=True)),
                ('score_a', models.IntegerField(default=None, null=True)),
                ('score_b', models.IntegerField(default=None, null=True)),
                ('next_id', models.IntegerField()),
                ('next_position', models.CharField(max_length=255)),
                ('stage', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('datetime', models.DateTimeField()),
                ('max_players', models.IntegerField()),
                ('status', models.CharField(max_length=255)),
            ],
        ),
    ]
