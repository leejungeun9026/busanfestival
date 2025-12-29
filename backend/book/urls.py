from django.urls import path, include
from rest_framework import routers 
from .views import BookViewSet

# 라우터 모델 가져오기
router = routers.DefaultRouter()
# 모델뷰셋을 라우터에 등록하기
router.register(r'books', BookViewSet, basename='book')

urlpatterns =  [
  path('', include(router.urls)),
]