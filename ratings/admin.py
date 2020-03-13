from django.contrib import admin
from .models import Rating

# Register your models here.

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score', 'last_update')

admin.site.register(Rating, RatingAdmin)
