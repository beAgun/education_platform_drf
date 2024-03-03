from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Status(models.IntegerChoices):
        tutor = 1, 'Преподаватель'
        student = 0, 'Студент'

    status = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                 default=Status.student, verbose_name='Статус')

    def __str__(self):
        return f'{self.username}'
