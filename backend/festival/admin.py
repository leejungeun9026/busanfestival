from __future__ import annotations
from django.apps import apps
from django.contrib import admin, messages
from django.core.management import call_command
from django.db import models
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import FestivalSyncLog, FestivalRaw, Festival


def _norm_text(v: str | None) -> str:
  # None/"" 동치 처리 + 줄바꿈 통일 + 끝 공백 제거
  if v is None:
      v = ""
  v = v.replace("\r\n", "\n")
  v = v.rstrip()
  return v



@admin.register(FestivalSyncLog)
class FestivalSyncLogAdmin(admin.ModelAdmin):
  list_display = (
    "id",
    "external_source",
    "sync_type",
    "status",
    "started_at",
    "finished_at",
    "total_count",
    "insert_count",
    "update_count",
    "skip_count",
    "error_count",
    "apply_status",
    "apply_insert_count",
    "apply_update_count",
    "apply_skip_count",
    "apply_error_count",
    "applied_at",
    "raw_file_path",
  )
  list_filter = ("external_source", "sync_type", "status", "apply_status")
  search_fields = ("id", "raw_file_path", "result_code", "result_msg", "note")
  ordering = ("-started_at",)

  readonly_fields = (
    "external_source",
    "sync_type",
    "status",
    "total_count",
    "insert_count",
    "update_count",
    "skip_count",
    "error_count",
    "started_at",
    "finished_at",
    "result_code",
    "result_msg",
    "request_rows",
    "triggered_by",
    "note",
    "raw_file_path",
    "raw_file_size",
    "raw_file_checksum",
    "apply_status",
    "apply_insert_count",
    "apply_update_count",
    "apply_skip_count",
    "apply_error_count",
    "applied_at",
  )

  fieldsets = (
    ("기본", {"fields": ("external_source", "sync_type", "triggered_by")}),
    ("SYNC 상태", {"fields": ("status", "started_at", "finished_at", "request_rows")}),
    ("SYNC 통계", {"fields": ("total_count", "insert_count", "update_count", "skip_count", "error_count")}),
    ("공공데이터 응답", {"fields": ("result_code", "result_msg", "note")}),
    ("원본 스냅샷", {"fields": ("raw_file_path", "raw_file_size", "raw_file_checksum")}),
    ("APPLY 상태", {"fields": ("apply_status", "applied_at")}),
    ("APPLY 통계", {"fields": ("apply_insert_count", "apply_update_count", "apply_skip_count", "apply_error_count")}),
  )

  # 읽기전용으로 만들기
  def has_add_permission(self, request):
    return False
  def has_change_permission(self, request, obj=None):
    return False
  def has_delete_permission(self, request, obj=None):
    return False
  
  # custom url 추가
  # /admin/festival/festivalsynclog/sync/
  # /admin/festival/festivalsynclog/apply/
  def get_urls(self) :
    urls = super().get_urls()
    custom_urls = [
      path(
        "sync/", 
        self.admin_site.admin_view(self.sync_view),
        name="festival_synclog_sync",
      ),
      path(
        "apply/",
        self.admin_site.admin_view(self.apply_view),
        name="festival_synclog_apply",
      ),
    ]
    return custom_urls + urls

  # sync(공공데이터 수집) 버튼 구현
  def sync_view(self, request) :
    try:
      call_command("sync_public_festivals")
      messages.success(request, "sync_public_festivals 실행")
    except Exception as e :
      messages.error(request, f"Sync 실행 실패: {e}")
    return redirect("..")

  # apply(동기화) 버튼 구현
  def apply_view(self, request) :
    sync_log = (
      FestivalSyncLog.objects
      .filter(status=FestivalSyncLog.Status.SUCCESS)
      .order_by("-finished_at")
      .first()
    )
    if not sync_log:
      messages.error(request, "적용할 SUCCESS SyncLog가 없습니다.")
      return redirect("..")
    
    try:
      call_command("apply_public_festivals", sync_log_id=sync_log.id)
      messages.success(request, "apply_public_festivals 실행")
    except Exception as e :
      messages.error(request, f"Apply 실행 실패: {e}")

    return redirect("..")


# FestivalSyncLog테이블 Read-only 설정
@admin.register(FestivalRaw)
class FestivalRawAdmin(admin.ModelAdmin):
  list_display = (
    "id", 
    "main_title", 
    "external_id", 
    "festival_link", 
    "last_synced_at", 
    "updated_at")
  list_display_links = ("main_title",)
  list_filter = ("external_source",)
  search_fields = ("main_title", "external_id",)
  ordering = ("-updated_at",)

  readonly_fields = (
    "external_source",
    "external_id",
    "payload",
    "payload_hash",
    "fetched_sync",
    "last_synced_at",
    "created_at",
    "updated_at",
    "festival_link",
  )

  fieldsets = (
    ("식별자", {"fields": ("external_source", "external_id")}),
    ("연결 정보", {"fields": ("fetched_sync", "last_synced_at", "festival_link")}),
    ("데이터", {"fields": ("main_title", "payload_hash", "payload")}),
    ("시각", {"fields": ("created_at", "updated_at")}),
  )

  def festival_link(self, obj):
    Festival = apps.get_model("festival", "Festival")
    if Festival is None:
        return "Festival 모델 없음"
    
    festival = Festival.objects.filter(
      external_source=obj.external_source,
      external_id=obj.external_id,
    ).first()

    if not festival:
        return "-"

    url = reverse(
      "admin:festival_festival_change",
      args=[festival.id],
    )
    return format_html('<a href="{}">운영 데이터 보기</a>', url)

  # 읽기전용으로 만들기
  def has_add_permission(self, request):
    return False
  def has_change_permission(self, request, obj=None):
    return False
  def has_delete_permission(self, request, obj=None):
    return False



@admin.register(Festival)
class FestivalAdmin(admin.ModelAdmin):
  list_display = (
    "id",
    "gugun_filter_link",
    "main_title_display",
    "external_id",
    "date_precision",
    "start_date",
    "end_date",
    "extra_schedule_note",
    "view_count",
    "is_visible",
    "is_deleted",
    "updated_at",
    "updated_by",
  )
  list_display_links = ("main_title_display",)
  list_filter = ("gugun_nm", "date_precision", "is_visible", "is_deleted")
  search_fields = ("main_title_display", "title", "place_raw", "addr1", "addr2", "external_id")
  ordering = ("-updated_at",)

  # 리스트에서 바로 토글 가능
  list_editable = ("is_visible", "is_deleted")

  # 텍스트/JSON 길어도 편하게
  formfield_overrides = {models.TextField: {"widget": admin.widgets.AdminTextareaWidget(attrs={"rows": 4})},
  }

  readonly_fields = (
    "external_source",
    "external_id",
    "payload_hash",
    "last_synced_sync",
    "main_title_raw",
    "place_raw",
    "main_place_raw",
    "usage_day",
    "usage_day_week_and_time",
    "main_img_thumb_preview",
    "created_at",
    "updated_at",
    "updated_by",
    "edited_fields",
  )

  fieldsets = (
    ("API 및 동기화 정보", {"fields": ("external_source", "external_id", "payload_hash", "last_synced_sync")}),
    ("노출/삭제", {"fields": ("is_visible", "is_deleted")}),
    ("원문 정보", {"fields": ("main_title_raw", "place_raw", "main_place_raw", "usage_day", "usage_day_week_and_time",)}),
    ("이미지", {"fields": ("main_img_thumb_preview", "main_img_normal", "main_img_thumb")}),
    ("필드 수정", {"fields": ("main_title_display", "title", "subtitle", "gugun_nm", "place_display","item_contents", "usage_amount","facilities", "view_count")}),
    ("주소/연락/링크 수정", {"fields": ("addr1", "addr2", "cntct_tel", "homepage_url")}),
    ("좌표/교통", {"fields": ("lat", "lng", "trfc_info")}),
    ("일정 수정", {"fields": ("start_date", "end_date", "date_precision", "extra_schedule_note")}),
    ("메타", {"fields": ("created_at", "updated_at", "updated_by", "edited_fields")}),
  )

  actions = ("action_mark_visible", "action_mark_hidden", "action_soft_delete", "action_restore")

  def gugun_filter_link(self, obj):
    if not obj.gugun_nm:
      return "-"

    changelist_url = reverse("admin:festival_festival_changelist")
    return format_html(
      '<a href="{}?gugun_nm={}">{}</a>',
      changelist_url,
      obj.gugun_nm,
      obj.gugun_nm,
    )
  gugun_filter_link.short_description = "gugun nm"

  def main_img_thumb_preview(self, obj):
    if not obj.main_img_thumb:
        return "이미지 없음"
    return format_html(
      '<img src="{}" style="max-width:200px; max-height:150px; border:1px solid #ddd;" />',
      obj.main_img_thumb
    )
  main_img_thumb_preview.short_description = "썸네일 미리보기"

  def save_model(self, request, obj, form, change):
    """
    Admin에서 수정된 필드를 edited_fields에 자동 누적
    - 최초 생성 시: edited_fields는 그대로(빈 리스트 유지)
    - 수정 시: form.changed_data 기반으로 누적
    """
    username = getattr(request.user, "username", None) or str(request.user)
    # 누가 수정했는지 기록
    obj.updated_by = username

    if change:
      changed = list(getattr(form, "changed_data", []) or [])

      # 저장 전 DB 원본 가져오기
      old = Festival.objects.get(pk=obj.pk)

      # item_contents는 노이즈 필드라 정규화 비교 후 같으면 변경에서 제거
      if "item_contents" in changed:
        if _norm_text(old.item_contents) == _norm_text(obj.item_contents):
          changed.remove("item_contents")
      
      # 관리용/자동 갱신 필드는 제외(
      exclude = {
        "updated_at",
        "updated_by",
        "edited_fields",
        "last_synced_sync",
        "payload_hash",
        "created_at",
      }

      changed = [f for f in changed if f not in exclude]

      # 기존 누적 목록 + 이번 변경 목록 (중복 제거, 순서 유지)
      current = list(obj.edited_fields or [])
      for f in changed:
        if f not in current:
          current.append(f)
      obj.edited_fields = current

    super().save_model(request, obj, form, change)


  @admin.action(description="선택 항목 노출(visible=True)")
  def action_mark_visible(self, request, queryset):
    queryset.update(is_visible=True, updated_at=timezone.now())

  @admin.action(description="선택 항목 숨김(visible=False)")
  def action_mark_hidden(self, request, queryset):
    queryset.update(is_visible=False, updated_at=timezone.now())

  @admin.action(description="선택 항목 소프트 삭제(is_deleted=True)")
  def action_soft_delete(self, request, queryset):
    queryset.update(is_deleted=True, updated_at=timezone.now())

  @admin.action(description="선택 항목 복구(is_deleted=False)")
  def action_restore(self, request, queryset):
    queryset.update(is_deleted=False, updated_at=timezone.now())