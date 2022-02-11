from django.views.generic import ListView, DetailView
from .models import Post


class PostList(ListView):
    model = Post # model을 정해 줌.
    ordering = '-pk'

class PostDetail(DetailView):
    model = Post