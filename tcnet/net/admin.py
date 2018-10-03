from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import Like, Post, TCUser

admin.site.register(TCUser)
admin.site.register(Post)
admin.site.register(Like)
