from rest_framework.serializers import ModelSerializer
from .models import Movie, MovieGenre, MovieCompany, MovieLanguage, MovieCountry, MovieActor, MovieDirector


class MovieActorSerializer(ModelSerializer):
    class Meta:
        model = MovieActor
        depth = 1
        fields = ['actor']

    def to_representation(self, instance):
        return instance.actor.name


class MovieGenreSerializer(ModelSerializer):
    class Meta:
        model = MovieGenre
        depth = 1
        fields = ['genre']

    def to_representation(self, instance):
        return instance.genre.name_kr


class MovieDirectorSerializer(ModelSerializer):
    class Meta:
        model = MovieDirector
        depth = 1
        fields = ['director']

    def to_representation(self, instance):
        return instance.director.name


class MovieCompanySerializer(ModelSerializer):
    class Meta:
        model = MovieCompany
        depth = 1
        fields = ['company']

    def to_representation(self, instance):
        return instance.company.name


class MovieLanguageSerializer(ModelSerializer):
    class Meta:
        model = MovieLanguage
        depth = 1
        fields = ['language']

    def to_representation(self, instance):
        return instance.language.name_kr


class MovieCountrySerializer(ModelSerializer):
    class Meta:
        model = MovieCountry
        depth = 1
        fields = ['country']

    def to_representation(self, instance):
        return instance.country.name_kr


class MovieSerializer(ModelSerializer):
    genres = MovieGenreSerializer(many=True, read_only=True)
    directors = MovieDirectorSerializer(many=True, read_only=True)
    actors = MovieActorSerializer(many=True, read_only=True)
    countries = MovieCountrySerializer(many=True, read_only=True)
    # languages = MovieLanguageSerializer(many=True, read_only=True)
    # companies = MovieCompanySerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'title_kr', 'release_year', 'runtime',
            'imdb_score', 'tmdb_score',
            'genres', 'directors', 'actors', 'countries',
        ]


class SimpleMovieSerializer(ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'title_kr', 'release_year',
        ]
