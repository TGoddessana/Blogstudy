from django.db import models
import os
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # 카테고리의 이름을 담는 필드, unique=True로 하여 같은 이름의 카테고리를 만들지 못하도록 함
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    # 슬러그 필드, allow_unicode=True로 한글도 사용할 수 있도록 함

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'

class Post(models.Model): # models 모듈의 Model 클래스를 상속해 만든 것.
    title = models.CharField(max_length=30)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d' , blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d' , blank=True)
    # 아래의 코드는 자동으로 생성일시, 수정일시를 표현할 수 있도록 해 줍니다.
    created_at = models.DateTimeField(auto_now_add=True) # 생성일자를 표현할 때: auto_now_add
    updated_at = models.DateTimeField(auto_now=True) # 수정일자를 표현할 때 : auto_now

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}' # 파이썬 3.6부터 생긴 포매팅 방법.

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get.file_name().split('.')[-1]