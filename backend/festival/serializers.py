from rest_framework import serializers
from .models import Festival

# 리스트 전용
class FestivalListSerializer(serializers.ModelSerializer):
  class Meta:
    model = Festival
    fields = [
      "id",
      "main_title_display",
      "gugun_nm",
      "lat",
      "lng",
      "place_display",
      "title",
      "subtitle",
      "addr1",
      "addr2",
      "cntct_tel",
      "homepage_url",
      "trfc_info",
      "date_precision",
      "start_date",
      "end_date",
      "extra_schedule_note",
      "usage_amount",
      "main_img_thumb",
      "middle_size_rm1"      
    ]

# 상세보기 전용
class FestivalDetailSerializer(serializers.ModelSerializer):
  class Meta:
    model = Festival
    fields = [
      "id",
      "main_title_display",
      "gugun_nm",
      "lat",
      "lng",
      "place_display",
      "title",
      "subtitle",
      "addr1",
      "addr2",
      "cntct_tel",
      "homepage_url",
      "trfc_info",
      "date_precision",
      "start_date",
      "end_date",
      "extra_schedule_note",
      "usage_amount",
      "main_img_normal",
      "item_contents",
      "middle_size_rm1"      
    ]