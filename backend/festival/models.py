from django.db import models
from django.utils import timezone


# 공공데이터 요청 로그 테이블
class FestivalSyncLog(models.Model):
  class SyncType(models.TextChoices):
    MANUAL = "MANUAL", "수동 요청"
    BATCH = "BATCH", "자동 요청"

  class Status(models.TextChoices):
    RUNNING = "RUNNING", "동기화 진행 중"
    SUCCESS = "SUCCESS", "전체 성공"
    PARTIAL = "PARTIAL", "일부 성공"
    FAIL = "FAIL", "전체 실패"

  external_source = models.CharField(max_length=50, default="PUBLIC_API") # 데이터 출처
  sync_type = models.CharField(max_length=20, choices=SyncType.choices, default=SyncType.MANUAL)
  status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)

  started_at = models.DateTimeField(default=timezone.now)
  finished_at = models.DateTimeField(null=True, blank=True)

  result_code = models.CharField(max_length=20, null=True, blank=True)
  result_msg = models.CharField(max_length=255, null=True, blank=True)
  request_rows = models.IntegerField(null=True, blank=True)

  total_count = models.IntegerField(null=True, blank=True)
  insert_count = models.IntegerField(default=0)
  update_count = models.IntegerField(default=0)
  skip_count = models.IntegerField(default=0)
  error_count = models.IntegerField(default=0)

  triggered_by = models.CharField(max_length=100)  # admin_id or system
  note = models.TextField(null=True, blank=True)

  class Meta:
    db_table = "festival_sync_log"
    verbose_name = "축제 데이터 동기화 로그"
    verbose_name_plural = "축제 데이터 동기화 로그 목록"
    ordering = ("-started_at",)



# 축제 데이터 원본
class FestivalPublic(models.Model):
  # 데이터 출처
  external_source = models.CharField(max_length=50, default="PUBLIC_API")
  # 데이터에서 제공하는 고유 아이디
  external_id = models.CharField(max_length=50)

  # 공공데이터 필드
  main_title = models.CharField(max_length=300, null=True, blank=True)
  gugun_nm = models.CharField(max_length=100, null=True, blank=True)
  lat = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
  lng = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
  place = models.CharField(max_length=300, null=True, blank=True)
  title = models.CharField(max_length=300, null=True, blank=True)
  subtitle = models.CharField(max_length=300, null=True, blank=True)
  main_place = models.CharField(max_length=100, null=True, blank=True)
  addr1 = models.CharField(max_length=200, null=True, blank=True)
  addr2 = models.CharField(max_length=200, null=True, blank=True)
  cntct_tel = models.CharField(max_length=200, null=True, blank=True)
  homepage_url = models.CharField(max_length=200, null=True, blank=True)
  trfc_info = models.CharField(max_length=500, null=True, blank=True)
  usage_day = models.CharField(max_length=500, null=True, blank=True)
  usage_day_week_and_time = models.CharField(max_length=500, null=True, blank=True)
  usage_amount = models.CharField(max_length=500, null=True, blank=True)
  main_img_normal = models.CharField(max_length=500, null=True, blank=True)
  main_img_thumb = models.CharField(max_length=500, null=True, blank=True)
  item_contents = models.TextField(null=True, blank=True)
  middle_size_rm1 = models.CharField(max_length=500, null=True, blank=True)

  # 데이터 중복 확인용 해시
  payload_hash = models.CharField(max_length=64, null=True, blank=True)  # sha256 hex 같은 걸 넣을 예정
  fetched_sync = models.ForeignKey(
    FestivalSyncLog, on_delete=models.PROTECT, related_name="public_rows"
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = "festival_public"
    verbose_name = "축제 데이터 원본"
    verbose_name_plural = "축제 데이터 원본 목록"
    constraints = [
      models.UniqueConstraint(
        fields=["external_source", "external_id"], name="uq_public_source_id"
      )
    ]
    ordering = ("-updated_at",)


# 축제 데이터 운영용
class FestivalAdmin(models.Model):
  class DatePrecision(models.TextChoices):
    EXACT = "EXACT", "특정일"
    RANGE_MONTH = "RANGE_MONTH", "월 범위"
    RANGE_YEAR = "RANGE_YEAR", "연 범위"
    TBD = "TBD", "추후 공지"
    ALWAYS = "ALWAYS", "상시"
    UNKNOWN = "UNKNOWN", "알 수 없음"

  external_source = models.CharField(max_length=50, default="PUBLIC_API")
  external_id = models.CharField(max_length=50)

  main_title = models.CharField(max_length=300, null=True, blank=True)
  gugun_nm = models.CharField(max_length=100, null=True, blank=True)
  lat = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
  lng = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
  place = models.CharField(max_length=300, null=True, blank=True)
  title = models.CharField(max_length=300, null=True, blank=True)
  subtitle = models.CharField(max_length=300, null=True, blank=True)
  main_place = models.CharField(max_length=100, null=True, blank=True)
  addr1 = models.CharField(max_length=200, null=True, blank=True)
  addr2 = models.CharField(max_length=200, null=True, blank=True)
  cntct_tel = models.CharField(max_length=200, null=True, blank=True)
  homepage_url = models.CharField(max_length=200, null=True, blank=True)
  trfc_info = models.CharField(max_length=500, null=True, blank=True)
  usage_day = models.CharField(max_length=500, null=True, blank=True)
  usage_day_week_and_time = models.CharField(max_length=500, null=True, blank=True)
  usage_amount = models.CharField(max_length=500, null=True, blank=True)
  main_img_normal = models.CharField(max_length=500, null=True, blank=True)
  main_img_thumb = models.CharField(max_length=500, null=True, blank=True)
  item_contents = models.TextField(null=True, blank=True)
  middle_size_rm1 = models.CharField(max_length=500, null=True, blank=True)

  start_date = models.DateField(null=True, blank=True)
  end_date = models.DateField(null=True, blank=True)
  date_precision = models.CharField(
      max_length=20, choices=DatePrecision.choices, default=DatePrecision.UNKNOWN
  )
  extra_schedule_note = models.CharField(max_length=500, null=True, blank=True)
  time_info_raw = models.CharField(max_length=500, null=True, blank=True)

  is_visible = models.BooleanField(default=True)
  is_deleted = models.BooleanField(default=False)

  edited_fields = models.JSONField(default=list)  # ["title","item_contents"]
  last_synced_sync = models.ForeignKey(
    FestivalSyncLog,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="admin_rows",
  )

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  updated_by = models.CharField(max_length=100, null=True, blank=True)

  class Meta:
    db_table = "festival_admin"
    verbose_name = "축제 데이터 운영용"
    verbose_name_plural = "축제 데이터 운영용 목록"
    constraints = [
      models.UniqueConstraint(
        fields=["external_source", "external_id"], name="uq_admin_source_id"
      )
    ]
    ordering = ("-updated_at",)
