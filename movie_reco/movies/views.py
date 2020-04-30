import logging

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.decorators import login_required
from movies.tmdb import poster_url
from recommender.reco_interface import RECO_INTERFACE
from .exceptions import UpdateFailed
from .models import Movie
from .serializers import SimpleMovieSerializer, MovieSerializer


logger = logging.getLogger('movie_api')


def run_update(movie):
    try:
        movie.update_from_tmdb()
    except UpdateFailed:
        logger.error(f"Couldn't get movie data from TMDB API: {movie.title} ({movie.release_year})")
    else:
        pass


@method_decorator(login_required, name='dispatch')
class MovieAPI(APIView):

    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        if movie.is_init_state or movie.is_older_than(1):
            run_update(movie)

        response_data = MovieSerializer(movie).data

        if movie.overview_kr:
            response_data['overview'] = movie.overview_kr
        else:
            response_data['overview'] = movie.overview

        if movie.use_alt_poster:
            response_data['poster'] = movie.alt_poster
        else:
            response_data['poster'] = poster_url(movie.poster)

        response_data['similar_items'] = RECO_INTERFACE.get_similar_items(movie, 12)

        json = JSONRenderer().render(response_data)
        return Response(json)


@method_decorator(login_required, name='dispatch')
class SimpleMovieAPI(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        if movie.is_init_state or movie.is_older_than(1):
            run_update(movie)

        response_data = SimpleMovieSerializer(movie).data

        if movie.use_alt_poster:
            response_data['poster'] = movie.alt_poster
        else:
            response_data['poster'] = poster_url(movie.poster)

        if not movie.overview_kr:
            response_data['title_kr'], response_data['title'] = response_data['title'], response_data['title_kr']

        json = JSONRenderer().render(response_data)
        return Response(json)
