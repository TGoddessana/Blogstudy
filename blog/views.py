from django.shortcuts import render
from .models import Post

def index(request):
    posts = Post.objects.all().order_by('-pk')
    # print(posts)
    # <QuerySet [<Post: [1] This is first post.>]>

    return render(
        request,
        'blog/post_list.html',
        {
            'posts': posts,
        }
    )

def single_post_page(request, pk): # pk도 매개변수로 받음.
    post = Post.objects.get(pk=pk) # pk가 매개변수로 받은 pk와 같은 레코드를 가져와라! 라는 의미
    # pk는 primary key

    return render(
        request,
        'blog/single_post_page.html',
        {
            'post':post, # 위에서 받아온 레코드
        }
    )