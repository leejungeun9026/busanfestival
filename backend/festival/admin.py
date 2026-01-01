from __future__ import annotations

from django.contrib import admin
from django.db import models
from django.utils import timezone

from .models import FestivalSyncLog, FestivalRaw, Festival


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



# FestivalSyncLog테이블 Read-only 설정
@admin.register(FestivalRaw)
class FestivalRawAdmin(admin.ModelAdmin):
  list_display = ("id", "external_source", "external_id", "fetched_sync", "last_synced_at", "updated_at")
  list_filter = ("external_source",)
  search_fields = ("external_id",)
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
  )

  fieldsets = (
    ("식별자", {"fields": ("external_source", "external_id")}),
    ("연결 정보", {"fields": ("fetched_sync", "last_synced_at")}),
    ("데이터", {"fields": ("payload_hash", "payload")}),
    ("시각", {"fields": ("created_at", "updated_at")}),
  )

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
    "external_source",
    "external_id",
    "main_title",
    "gugun_nm",
    "start_date",
    "end_date",
    "date_precision",
    "is_visible",
    "is_deleted",
    "last_synced_sync",
    "updated_at",
    "updated_by",
  )
  list_filter = ("external_source", "gugun_nm", "date_precision", "is_visible", "is_deleted")
  search_fields = ("main_title", "title", "place", "addr1", "addr2", "external_id")
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
    "created_at",
    "updated_at",
    "updated_by",
    "edited_fields",
  )

  fieldsets = (
    ("식별자", {"fields": ("external_source", "external_id", "payload_hash", "last_synced_sync")}),
    ("노출/삭제", {"fields": ("is_visible", "is_deleted")}),
    ("기본 정보", {"fields": ("main_title", "title", "subtitle", "gugun_nm", "place", "main_place")}),
    ("주소/연락/링크", {"fields": ("addr1", "addr2", "cntct_tel", "homepage_url")}),
    ("좌표/교통", {"fields": ("lat", "lng", "trfc_info")}),
    ("원문 일정", {"fields": ("usage_day", "usage_day_week_and_time", "usage_amount")}),
    ("정규화 일정(운영)", {"fields": ("start_date", "end_date", "date_precision", "time_info_raw", "extra_schedule_note")}),
    ("이미지/설명", {"fields": ("main_img_normal", "main_img_thumb", "item_contents", "middle_size_rm1")}),
    ("메타", {"fields": ("created_at", "updated_at", "updated_by", "edited_fields")}),
  )

  actions = ("action_mark_visible", "action_mark_hidden", "action_soft_delete", "action_restore")

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
      # form.changed_data: 이번 저장에서 실제로 변경된 필드명 리스트
      changed = list(getattr(form, "changed_data", []) or [])

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