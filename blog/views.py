from django.shortcuts import render
from django.views.generic import ListView
from .models import Post


class PostList(ListView):
    model = Post # model을 정해 줌.
    ordering = '-pk'