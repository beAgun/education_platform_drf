from abc import ABC

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import *


class ProductSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    start_date = serializers.DateTimeField()
    price = serializers.DecimalField(max_digits=8, decimal_places=2)
    lessons = serializers.IntegerField()
    author__username = serializers.CharField()


class ProductStatisticsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    start_date = serializers.DateTimeField()
    #price = serializers.DecimalField(max_digits=8, decimal_places=2)
    #lessons = serializers.IntegerField()
    #author__username = serializers.CharField()
    num_students = serializers.IntegerField()
    occupancy = serializers.FloatField()
    acquisition = serializers.FloatField()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Product
        fields = '__all__'


class ProductLessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = 'title', 'video'


class UserSerializer(serializers.ModelSerializer):

    password1 = serializers.CharField(write_only=True, label='Пароль')
    password2 = serializers.CharField(write_only=True, label='Потверждение пароля')

    def create(self, validated_data):
        if validated_data['password1'] != validated_data['password2']:
            raise ValidationError('Пароли не совпадают')

        if validated_data['email'] and get_user_model().objects.filter(email=validated_data['email']).exists():
            raise ValidationError('Пользователь с таким E-mail уже существует.')

        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password1'],
        )
        return user

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'status', 'password1', 'password2')


class GroupSerializer(serializers.ModelSerializer):

    #students = serializers.ListField()

    class Meta:
        model = Group
        fields = ('product', 'reserved_group', 'id', 'title', 'students')

