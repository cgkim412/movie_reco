from django.db import models


class Rating(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE,
                             related_name='ratings', verbose_name="User")
    movie = models.ForeignKey("movies.Movie", on_delete=models.CASCADE,
                              related_name='ratings', verbose_name="Movie")

    VALID_SCORES = [0.5 * i for i in range(1, 11)]
    VALID_SCORE_CHOICES = [(0.5 * i, str(0.5 * i)) for i in range(1, 11)]
    score = models.DecimalField(max_digits=2, decimal_places=1, verbose_name="User's rating",
                                choices=VALID_SCORE_CHOICES)
    last_update = models.DateTimeField(auto_now=True, verbose_name="Last updated on")

    def __str__(self):
        return f"({self.movie}, {self.score})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name="User rating")
        ]

        ordering = ['-score']

