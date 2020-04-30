from datetime import datetime, timezone

import requests
from django.db import models

from metadata.models import Country, Language, Company, Genre
from .exceptions import UpdateFailed
from .tmdb import api_url


class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True, verbose_name="TMDB ID")
    imdb_id = models.CharField(unique=True, max_length=16, verbose_name="IMDB ID")

    title = models.CharField(max_length=64, verbose_name="Movie title (original)")
    title_kr = models.CharField(max_length=64, verbose_name="Movie title (Korean)")

    release_date = models.DateField(null=True, verbose_name="Release date")
    release_year = models.IntegerField(null=True, verbose_name="Release year")

    runtime = models.IntegerField(null=True, verbose_name="Running time")
    tagline = models.CharField(max_length=255, verbose_name="Tag line")
    overview = models.TextField(verbose_name="Plot overview (EN)")
    overview_kr = models.TextField(verbose_name="Plot overview (KR)")

    poster = models.TextField(null=True, verbose_name="poster URL")
    alt_poster = models.TextField(verbose_name="Alt. poster URL")

    imdb_score = models.DecimalField(null=True, max_digits=2, decimal_places=1, verbose_name="IMDB avg. score")
    imdb_votes = models.IntegerField(null=True, verbose_name="# of IMDB votes")

    tmdb_score = models.DecimalField(null=True, max_digits=2, decimal_places=1, verbose_name="TMDB avg. score")
    tmdb_votes = models.IntegerField(null=True, verbose_name="# of TMDB votes")
    tmdb_popularity = models.FloatField(null=True, verbose_name="TMDB Popularity (daily)")

    is_init_state = models.BooleanField(default=True, verbose_name="Is initial state?")
    use_alt_poster = models.BooleanField(default=True, verbose_name="Use alternate poster?")
    last_update = models.DateTimeField(auto_now=True, verbose_name="Last updated on")

    def __str__(self):
        return self.title

    def is_older_than(self, days: int):
        return (datetime.now(timezone.utc) - self.last_update).days >= days

    def update_from_tmdb(self, force_update=False):
        response = requests.get(api_url(self.tmdb_id))

        if not response.ok:
            raise UpdateFailed

        data = response.json()

        if self.is_init_state or force_update:
            self.title_kr = data['title']
            self.release_date = data['release_date']

            self.tagline = data['tagline']
            self.overview_kr = data['overview']

            # delete initial movie_genre data
            MovieGenre.objects.filter(movie=self).all().delete()
            for entry in data['genres']:
                genre = Genre.objects.get(id=entry['id'])
                MovieGenre.objects.get_or_create(movie=self, genre=genre)

            for entry in data['spoken_languages']:
                try:
                    language = Language.objects.get(code=entry['iso_639_1'])
                except Language.DoesNotExist:
                    continue
                else:
                    MovieLanguage.objects.get_or_create(movie=self, language=language)

            for entry in data['production_countries']:
                try:
                    country = Country.objects.get(code=entry['iso_3166_1'])
                except Country.DoesNotExist:
                    continue
                else:
                    MovieCountry.objects.get_or_create(movie=self, country=country)

            for entry in data['production_companies']:
                try:
                    company = Company.objects.get(id=entry['id'])
                except Company.DoesNotExist:
                    company = Company(id=entry['id'], name=entry['name'])
                    company.save()
                finally:
                    MovieCompany.objects.get_or_create(movie=self, company=company)

            self.is_init_state = False

        self.poster = data['poster_path']
        self.tmdb_score = data['vote_average']
        self.tmdb_votes = data['vote_count']
        self.tmdb_popularity = data['popularity']

        if self.overview_kr:
            self.use_alt_poster = False

        self.save()


class MovieLanguage(models.Model):
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name="languages", verbose_name="Movie")
    language = models.ForeignKey("metadata.Language", on_delete=models.CASCADE, verbose_name="Language")

    def __str__(self):
        return self.language.name_kr

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['movie', 'language'], name='Movie language')
        ]


class MovieCountry(models.Model):
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name="countries", verbose_name="Movie")
    country = models.ForeignKey("metadata.Country", on_delete=models.CASCADE, verbose_name="Country")

    def __str__(self):
        return self.country.name_kr

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['movie', 'country'], name='Movie country')
        ]


class MovieGenre(models.Model):
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name="genres", verbose_name="Movie")
    genre = models.ForeignKey("metadata.Genre", on_delete=models.CASCADE, verbose_name="Genre")

    def __str__(self):
        return self.genre.name_kr

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['movie', 'genre_id'], name='Movie genre')
        ]


class MovieCompany(models.Model):
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name="companies", verbose_name="Movie")
    company = models.ForeignKey("metadata.Company", on_delete=models.CASCADE, verbose_name="Production company")

    def __str__(self):
        return self.company.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['movie', 'company'], name='Movie company')
        ]


class MovieActor(models.Model):
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name="actors", verbose_name="Movie")
    actor = models.ForeignKey("metadata.Person", on_delete=models.CASCADE, verbose_name="Actor")

    def __str__(self):
        return self.actor.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['movie', 'actor'], name='Movie actor')
        ]


class MovieDirector(models.Model):
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name="directors", verbose_name="Movie")
    director = models.ForeignKey("metadata.Person", on_delete=models.CASCADE, verbose_name="Director")

    def __str__(self):
        return self.director.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['movie', 'director'], name='Movie director')
        ]