from django.urls import path
from . import views # 같은 디렉토리의 views를 import

urlpatterns = [
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view())
]