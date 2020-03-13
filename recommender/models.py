from django.db import models


class Similarity(models.Model):
    """
    precomputed for performance
    """
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE, related_name="similar_items")
    other_movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE)
    score = models.FloatField(verbose_name="Similarity")

    def __str__(self):
        return f"({self.other_movie}, {self.score})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["movie", "other_movie"], name="similarity")
        ]
        ordering = ["-score"]
