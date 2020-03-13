from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Rating

class RatingSerializer(ModelSerializer):
    rating_count = SerializerMethodField()

    class Meta:
        model = Rating
        fields = ['movie', 'score', 'rating_count']

    def get_rating_count(self, obj):
        return Rating.objects.filter(user=obj.user).count()
