import random

from django.contrib.auth import get_user_model
from django.db.models import Count, ObjectDoesNotExist, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Like, Post
from .serializers import ActiveUserSerializer, LikeSerializer, PostSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False)
    def get_most_active(self, request, *args, **kwargs):

        users = get_user_model().objects. \
            annotate(num_posts=Count('posts')). \
            annotate(num_likes=Count('posts__likes')). \
            order_by('-num_posts')

        max_likes_per_user = request.GET.get('max_likes_per_user')

        if max_likes_per_user:
            users = users.filter(num_likes__lt=max_likes_per_user)

        serializer = ActiveUserSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def like_random_post(self, request, *args, **kwargs):

        user_id = request.data.get('user_id')

        try:
            user = get_user_model().objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        users_to_like = Post.objects.annotate(cnt=Count('likes')).filter(likes__id__isnull=True). \
            exclude(user_id=user.id, ).values('user_id').distinct()

        posts_to_like = Post.objects. \
            exclude(Q(user_id=user.id) | Q(likes__user_id=user.id)). \
            filter(user_id__in=users_to_like). \
            values('id')

        if len(posts_to_like) > 0:

            post_id = random.choice(posts_to_like)['id']
            print("\nTrying to like post #{} for user #{}".format(post_id, user.id))
            like = Like(post_id=post_id, user_id=user.id)
            like.save()
            return Response({'status': post_id}, status=200)
        else:
            return Response({'status': None}, status=304)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
