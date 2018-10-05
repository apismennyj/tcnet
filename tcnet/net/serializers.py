import clearbit
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Like, Post


class ActiveUserSerializer(serializers.ModelSerializer):
    num_posts = serializers.IntegerField()
    num_likes = serializers.IntegerField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'num_posts', 'num_likes')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'url', 'username', 'password', 'email', 'additional_data')

    def validate_email(self, value):
        """
        Check that email has correct format and deliverable
        """
        response = requests.get(settings.HUNTER_IO_URL.format(value, settings.HUNTER_IO_KEY))

        if response.status_code == 200:
            data = response.json()
            if data['data']['result'] != 'undeliverable':
                return value

        raise serializers.ValidationError("Email doesn't exist")

    def create(self, validated_data):

        created_user = super(UserSerializer, self).create(validated_data)

        if settings.CLEARBIT_ENABLED:
            clearbit.key = settings.CLEARBIT_KEY
            response = clearbit.Enrichment.find(email=created_user.email, stream=True)

            if response and response['person'] is not None:
                created_user.additional_data = response
                created_user.save()

        return created_user


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'user', 'body', 'date_published')


class LikeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user', 'post', 'date_published')
