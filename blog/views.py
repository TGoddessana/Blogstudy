from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify


# 태그 오류 수정 전.

class PostList(ListView):
    model = Post  # model을 정해 줌.
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')  # 템플릿에서 태그를 읽어옴
            if tags_str:  # 태그가 채워져 있으면
                tags_str = tags_str.strip()  # 양쪽의 공백 제거

                if tags_str[-1] == ";":  # 공백태그 이슈 해결?
                    tags_str = tags_str[:-1]

                tags_str = tags_str.replace(',', ';')  # , 를 ; 로 대체
                tags_list = tags_str.split(';')  # ;를 기준으로 나눔

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response

        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    template_name = 'blog/post_update_form.html'

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)

        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:  # 태그가 채워져 있으면
            tags_str = tags_str.strip()  # 양쪽의 공백 제거

            if tags_str[-1] == ";":  # 공백태그 이슈 해결?
                tags_str = tags_str[:-1]

            tags_str = tags_str.replace(',', ';')  # , 를 ; 로 대체
            tags_list = tags_str.split(';')  # ;를 기준으로 나눔

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)

        return response


def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )


# FBV
def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'tag': tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )

# FBV
def new_comment(request, pk):
    if request.user.is_authenticated:  # 로그인하지 않은 경우에는 접근하지 못하도록
        post = get_object_or_404(Post, pk=pk)  # pk가 없는 경우에는 404 에러 발생

        if request.method == 'POST': # 폼에서 요청해온 방식이라면
            comment_form = CommentForm(request.POST) # POST 정보로 얻어온 정보를 담음
            if comment_form.is_valid(): # 폼이 유요하다면 DB에 저장
                comment = comment_form.save(commit=False) # 바로 DB에 저장하지 않음
                comment.post = post # 댓글의 외래키로 연결된 포스트는 pk로 가져온 포스트가 됨
                comment.author = request.user # 로그인한 사람의 정보로 저자 정보 채우기
                comment.save()
                return redirect(comment.get_absolute_url())
            else:
                return redirect(post.get_absolute_url()) # 브라우저에 입력해서 들어오면 포스트 페이지로 리다이렉트
        else:
            raise PermissionDenied


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def delete_comment(request,pk): # 삭제 요청과 pk값을 인자로 받는다.
    comment = get_object_or_404(Comment, pk=pk) # pk로 댓글을 가져오거나 HTTP404를 발생시킨다.
    post = comment.post # 삭제하려는 댓글의 post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied