import clearbit
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Like, Post


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'password', 'email', 'additional_data')

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

        clearbit.key = settings.CLEARBIT_KEY
        response = clearbit.Enrichment.find(email=created_user.email, stream=True)

        if response['person'] is not None:
            created_user.additional_data = response
            created_user.save()

        return created_user


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('user', 'body', 'date_published')


class LikeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Like
        fields = ('user', 'post', 'date_published')
