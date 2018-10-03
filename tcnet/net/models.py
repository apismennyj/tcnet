from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class TCUser(AbstractUser):
    additional_data = models.TextField(null=True)
    email = models.EmailField('email address', blank=False, unique=True)

    def __str__(self):
        return "{} {} ({})".format(self.first_name, self.last_name, self.email)


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    date_published = models.DateTimeField('Post date', auto_now=True)

    def __str__(self):
        return "{}... ({} at {})".format(self.body[:50], self.user.last_name, self.date_published)


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    date_published = models.DateTimeField('Like date', auto_now=True)

    class Meta:
        unique_together = (("user", "post"),)

    def __str__(self):
        return "{} at {} for '{}'".format(self.user.last_name, self.date_published, self.post.body[:50])
