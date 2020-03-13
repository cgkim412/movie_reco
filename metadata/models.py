from django.db import models


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True, verbose_name="ISO-3166-1 alpha-2")
    name = models.CharField(max_length=64, verbose_name="Country name")
    name_kr = models.CharField(max_length=64, verbose_name="Country name (KR)")

    def __str__(self):
        return self.name_kr


class Language(models.Model):
    code = models.CharField(max_length=2, unique=True, verbose_name="ISO-639-1 alpha-2")
    name = models.CharField(max_length=64, verbose_name="Language name")
    name_kr = models.CharField(max_length=64, verbose_name="Language name (KR)")

    def __str__(self):
        return self.name_kr


class Genre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32, verbose_name="Genre name")
    name_kr = models.CharField(max_length=32, verbose_name="Genre name (KR)")

    def __str__(self):
        return self.name_kr


class Person(models.Model):
    imdb_id = models.CharField(max_length=16, verbose_name="IMDB ID", unique=True)
    name = models.CharField(max_length=128, verbose_name="Person's name")

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=128, verbose_name="Company name")

    def __str__(self):
        return self.name
