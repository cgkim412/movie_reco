from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .exceptions import UpdateFailed
from accounts.decorators import login_required
from .models import Movie
from .serializers import SimpleMovieSerializer, MovieSerializer
import logging
from django.http.response import HttpResponse
from recommender.reco_interface import RECO_INTERFACE
from django.urls import reverse

logger = logging.getLogger('movie_api')


def run_update(movie):
        try:
            movie.update_from_tmdb()
        except UpdateFailed:
            logger.error(f"Couldn't get movie data from TMDB API: {movie.title} ({movie.release_year})")
        else:
            pass
            # print(f"Update result: tmdb_ok = {movie.tmdb_ok}")

@method_decorator(login_required, name='dispatch')
class MovieAPI(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        # print(f"Movie data requested: {movie.title} ({movie.release_year}) | init state: {movie.is_init_state}")
        if movie.is_init_state:
            run_update(movie)

        response_data = MovieSerializer(movie).data

        if movie.overview_kr:
            response_data['overview'] = movie.overview_kr
            response_data['poster'] = reverse('poster') + str(movie.id)
        else:
            response_data['overview'] = movie.overview
            response_data['poster'] = movie.alt_poster

        response_data['similar_items'] = RECO_INTERFACE.get_similar_items(movie, 12)

        json = JSONRenderer().render(response_data)
        return Response(json)


@method_decorator(login_required, name='dispatch')
class SimpleMovieAPI(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)

        # print(f"Movie data requested: {movie.title} ({movie.release_year}) | init state: {movie.is_init_state}")
        if movie.is_init_state:
            run_update(movie)

        response_data = SimpleMovieSerializer(movie).data

        if movie.overview_kr:
            response_data['poster'] = reverse('poster') + str(movie.id)
        else:
            response_data['poster'] = movie.alt_poster

        json = JSONRenderer().render(response_data)
        return Response(json)


@method_decorator(login_required, name='dispatch')
class MoviePosterAPI(APIView):
    def get(self, request, movie_id):
        movie = get_object_or_404(Movie, id=movie_id)
        if movie.poster:
            return HttpResponse(movie.poster.read(), content_type="image/jpg")
        else:
            return HttpResponse(status=404)
