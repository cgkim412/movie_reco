from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Rating

class RatingSerializer(ModelSerializer):

    class Meta:
        model = Rating
        fields = ['movie', 'score']
