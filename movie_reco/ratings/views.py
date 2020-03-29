from django.shortcuts import render
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.decorators import login_required
from accounts.models import User
from movies.models import Movie
from .models import Rating
from .serializers import RatingSerializer
from recommender.reco_interface import RECO_INTERFACE


@login_required
def evaluate(request):
    user = User.objects.get(id=request.session.get('user'))
    eval_list = RECO_INTERFACE.get_eval_list(user, limit=200)
    json = JSONRenderer().render(eval_list)
    rating_count = user.ratings.all().count()
    return render(request, 'evaluate.html', {'rating_count': rating_count, 'eval_list': json.decode('utf8')})


@login_required
def my_ratings(request):
    user = User.objects.get(id=request.session.get('user'))
    serialized_data = RatingSerializer(user.ratings.all(), many=True).data
    json = JSONRenderer().render(serialized_data)
    return render(request, 'eval_record.html',
                  {'rating_count': user.ratings.all().count(), 'record': json.decode('utf8')})


@method_decorator(login_required, name='dispatch')
class RatingAPI(APIView):
    parser_classes = [JSONParser]

    def rating_to_json(self, obj):
        serialized_data = RatingSerializer(obj).data
        serialized_data['rating_count'] = obj.user.ratings.count()
        return JSONRenderer().render(serialized_data)

    def get(self, request, movie_id):
        movie = Movie.objects.get(id=movie_id)
        try:
            rating = Rating.objects.get(user=request.session.get('user'), movie=movie)
        except Rating.DoesNotExist:
            return Response(status=404)
        else:
            json = self.rating_to_json(rating)
            return Response(json)

    def post(self, request, movie_id):

        # validate the data
        try:
            score = request.data['score']
        except KeyError:
            return Response(status=400)
        else:
            if score not in Rating.VALID_SCORES:
                return Response(status=400)

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(status=404)

        user_id = request.session.get('user')
        user = User.objects.get(id=user_id)

        try:
            rating = Rating.objects.get(user=user, movie=movie)
        except Rating.DoesNotExist:
            rating = Rating.objects.create(user=user, movie=movie, score=score)
        else:
            if rating.score != score:
                rating.score = score
                rating.save()

        json = self.rating_to_json(rating)
        return Response(json)

    def delete(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(status=204)

        user_id = request.session.get('user')
        user = User.objects.get(id=user_id)

        try:
            rating = Rating.objects.get(user=user, movie=movie)
        except Rating.DoesNotExist:
            pass
        else:
            rating.delete()
        finally:
            empty_rating = Rating(user=user, movie=movie, score=None)
            json = self.rating_to_json(empty_rating)
            return Response(json)

