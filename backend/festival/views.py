from django.shortcuts import get_object_or_404
from django.db.models import F

from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Festival
from .serializers import FestivalListSerializer, FestivalDetailSerializer
from .pagination import FestivalPagination
from .filters import FestivalFilter



# Swagger에 노출할 쿼리 파라미터 정의
page_param = openapi.Parameter(
  "page",
  openapi.IN_QUERY,
  description="페이지 번호",
  type=openapi.TYPE_INTEGER,
)

size_param = openapi.Parameter(
  "size",
  openapi.IN_QUERY,
  description="페이지당 개수 (최대 100)",
  type=openapi.TYPE_INTEGER,
)


class FestivalViewSet(ReadOnlyModelViewSet):
  queryset = Festival.objects.all()
  
  # ?page=,size=적용
  pagination_class = FestivalPagination

  # 검색/필터/정렬 백엔드
  filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
  filterset_class = FestivalFilter

  # 필터 검색
  # DB필드 기준 정확히 매칭
  filterset_fields = [
    "gugun_nm",
  ]

  # 키워드 검색: ?search=부산
  # DB필드 기준 LIKE(contains) 검색 개념
  search_fields = [
    "main_title_display",
    "title",
    "subtitle",
    "place_display",
  ]

  # 정렬: ?ordering=start_date 또는 ?ordering=-start_date
  ordering_fields = [
    "start_date",
    "end_date"
  ]
  ordering = ["-id"]

  def get_serializer_class(self):
    if self.action == "list":
      return FestivalListSerializer
    return FestivalDetailSerializer

  # swagger에 파라미터 추가
  @swagger_auto_schema(manual_parameters=[page_param, size_param])
  def list(self, request, *args, **kwargs):
    print("paginator:", type(self.paginator))
    print("page_size_query_param:", getattr(self.paginator, "page_size_query_param", None))
    return super().list(request, *args, **kwargs)
  
  # 조회수 증가
  def retrieve(self, request, *args, **kwargs):
    # 1개 가져오기
    festival = self.get_object()

    # 조회수 증가
    Festival.objects.filter(pk=festival.pk).update(
      view_count=F("view_count") + 1
    )

    # DB에서 최신 Festival 정보 가져오기
    festival.refresh_from_db(fields=["view_count"])

    # Festival 객체를 응답(JSON)으로 보내기 위해 직렬화
    serializer = self.get_serializer(festival)
    return Response(serializer.data)