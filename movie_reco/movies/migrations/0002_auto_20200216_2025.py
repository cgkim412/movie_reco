# Generated by Django 3.0.1 on 2020-02-16 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='imdb_votes',
            field=models.IntegerField(null=True, verbose_name='# of IMDB votes'),
        ),
        migrations.AddField(
            model_name='movie',
            name='tmdb_votes',
            field=models.IntegerField(null=True, verbose_name='# of TMDB votes'),
        ),
    ]