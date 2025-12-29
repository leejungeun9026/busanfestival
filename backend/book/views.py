from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Book
from .serializers import BookSerializer


## 함수 기반 뷰로 단일 앤드포인트 생성 시
## Response 직접 만들어서 반환해줘야 함
# 
# @api_view(['POST'])
# def create_book(request):
#   serializer = BookSerializer(data=request.data)
#   if serializer.is_valid():
#     serializer.save()
#     return Response(serializer.data, status=201)
#   return Response(serializer.errors, status=400)


## viewSet 사용 시
## 사용자 정의 동작 추가하려면 @action 데코레이터 필수
## Response 직접 만들어서 반환해줘야 함
# 
# class BookViewSet(viewsets.ViewSet):
#   def list(self, request):
#     queryset = Book.objects.all()
#     serializer = BookSerializer(queryset, many=True)
#     return Response(serializer.data)
#   def retrieve(self, request, pk=None):
#     book = get_object_or_404(Book, pk=pk)
#     serializer = BookSerializer(book)
#     return Response(serializer.data)
#   @action(detail=True, methods=['post'])
#   def mark_as_read(self, request, pk=None):
#     book = get_object_or_404(Book, pk=pk)
#     book.mark_as_read()
#     return Response({'status': 'book marked as read'})


## ModelViewSet 사용 시
# 모델뷰셋을 상속받으면 CRUD 기본 액션을 자동 제공함
# GET	    /books/	      list()
# POST	  /books/	      create()
# GET	    /books/{id}/	retrieve()
# PUT	    /books/{id}/	update()
# PATCH	  /books/{id}/	partial_update()
# DELETE  /books/{id}/  destroy()
# 
# Response, is_valid() 자동 생성
# urls.py의 라우터에 작성한 이름으로 앤드포인트 생성됨
# router.register(r'book', BookViewSet, basename='book')

class BookViewSet(viewsets.ModelViewSet):
  # modelViewset은 반드시 아래 두가지 정보 필요
  # 어떤 모델을 대상으로 할지
  queryset = Book.objects.all()
  # 어떻게 직렬화/역직렬화 할지
  serializer_class = BookSerializer

  # 페이지네이션 활성화
  # PageNumberPagination모듈로 페이지네이션 설정함
  pagination_class = PageNumberPagination

  # 모델에 필터링, 정렬 활성화
  filter_backends = [SearchFilter, OrderingFilter]
  # /books/?search=django
  search_fields = ['title', 'author']
  # /books/?ordering=-publication_date
  ordering_fields = ['publication_date', 'price']

  # 사용자 정의 필터링 및 정렬 구현
  def get_queryset(self):
    queryset = super().get_queryset()
    # 요청에서 필터링 매개변수 가져오기
    title = self.request.query_params.get('title', None)
    author = self.request.query_params.get('author', None)

    # 필터링 적용
    if title:
      queryset = queryset.filter(title__icontains=title)
    if author:
      queryset = queryset.filter(author__icontains=author)

    # 정렬 적용
    ordering = self.request.query_params.get('ordering', None)
    if ordering in self.ordering_fields:
      queryset = queryset.order_by(ordering)

    return queryset