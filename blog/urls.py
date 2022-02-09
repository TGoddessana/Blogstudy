from django.urls import path
from . import views # 같은 디렉토리의 views를 import

urlpatterns = [
    path('', views.index), # blog/ 면 views의 index() 함수를 수행
]