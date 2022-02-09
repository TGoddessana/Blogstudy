from django.shortcuts import render
from .models import Post

def index(request):
    posts = Post.objects.all().order_by('-pk')
    # print(posts)
    # <QuerySet [<Post: [1] This is first post.>]>


    return render(
        request,
        'blog/index.html',
        {
            'posts': posts,
        }
    )