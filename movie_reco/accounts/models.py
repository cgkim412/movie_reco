from django.db import models


class User(models.Model):
    ADMIN = 0
    USER = 1
    BOT = 2
    email = models.EmailField(verbose_name="User email", unique=True)
    password = models.CharField(max_length=128, verbose_name="User password")
    type = models.IntegerField(verbose_name='User type',
        choices=(
            (ADMIN, 'admin'),
            (USER, 'user'),
            (BOT, 'bot')
        ))

    def __str__(self):
        return self.email

