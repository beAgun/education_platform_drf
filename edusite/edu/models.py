from django.contrib.auth import get_user_model
from django.db import models


class Product(models.Model):
    objects = models.Manager()

    class Rule(models.IntegerChoices):
        default = 1, 'По умолчанию'
        smart = 0, 'Умное'

    title = models.CharField(max_length=255, unique=True, verbose_name='Название')
    start_date = models.DateTimeField(verbose_name='Дата и время начала')
    price = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Цена')
    min_group_students_qty = models.PositiveSmallIntegerField(verbose_name='Минимальное количество студентов в группе')
    max_group_students_qty = models.PositiveSmallIntegerField(verbose_name='Максимальное количество студентов в группе')
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name='Автор')
    students = models.ManyToManyField(to=get_user_model(), through='Enrollment',
                                      related_name='products', verbose_name='Студенты')
    rule = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Rule.choices)),
                               default=Rule.default, verbose_name='Правило распределения по группам')

    def lesson_set_cnt(self):
        return len(self.lesson_set.count())

    def __str__(self):
        return f'{self.title}'


class Enrollment(models.Model):
    objects = models.Manager()

    class Permission(models.IntegerChoices):
        accessed = 1, 'Доступно'
        denied = 0, 'Не доступно'

    student = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name='Студент')
    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, verbose_name='Курс')
    permission = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Permission.choices)),
                                     default=Permission.denied, verbose_name='Разрешение на доступ')
    is_reserved = models.BooleanField(default=False, verbose_name='Запас')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата поступления')


class Lesson(models.Model):
    objects = models.Manager()

    title = models.CharField(max_length=255, verbose_name='Название')
    video = models.URLField(max_length=255, unique=True, verbose_name='Ссылка на видео')
    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, verbose_name='Курс')

    def __str__(self):
        return f'{self.title}'


def get_title(instance):
    return f'group_{instance.id}'


class Group(models.Model):
    objects = models.Manager()

    product = models.ForeignKey(to='Product', on_delete=models.CASCADE, verbose_name='Курс')
    students = models.JSONField(verbose_name='Студенты')
    title = models.CharField(max_length=255, default='group', verbose_name='Название')
    is_full = models.BooleanField(default=False, verbose_name='Полностью заполнена')
    reserved_group = models.BooleanField(verbose_name='Неполная группа(запас)')

    def __str__(self):
        return f'{self.title}'
