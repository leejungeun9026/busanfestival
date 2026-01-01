from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from festival.models import Festival, FestivalRaw, FestivalSyncLog
from festival.utils.data_normalize import normalize_schedule


# 의미 없는 공백 문자열을 None으로 저장
def _safe_str(v: Any) -> Optional[str]:
	if v is None:
		return None
	s = str(v).strip()
	return s if s != "" else None


def _safe_decimal(v: Any) -> Optional[Decimal]:
	if v is None or v == "":
		return None
	try:
		return Decimal(str(v).strip())
	except (InvalidOperation, ValueError, TypeError):
		return None


# FestivalRaw.payload(JSON) -> Festival(운영) 필드 매핑
def _map_payload_to_festival_fields(payload: Dict[str, Any]) -> Dict[str, Any]:
	usage_day = _safe_str(payload.get("USAGE_DAY"))
	usage_day_week_and_time = _safe_str(payload.get("USAGE_DAY_WEEK_AND_TIME"))

	sch = normalize_schedule(
		usage_day=usage_day,
		usage_day_week_and_time=usage_day_week_and_time,
	)

	return {
		# 공공데이터 필드 매핑
		"main_title": _safe_str(payload.get("MAIN_TITLE")),
		"gugun_nm": _safe_str(payload.get("GUGUN_NM")),
		"lat": _safe_decimal(payload.get("LAT")),
		"lng": _safe_decimal(payload.get("LNG")),
		"place": _safe_str(payload.get("PLACE")),
		"title": _safe_str(payload.get("TITLE")),
		"subtitle": _safe_str(payload.get("SUBTITLE")),
		"main_place": _safe_str(payload.get("MAIN_PLACE")),
		"addr1": _safe_str(payload.get("ADDR1")),
		"addr2": _safe_str(payload.get("ADDR2")),
		"cntct_tel": _safe_str(payload.get("CNTCT_TEL")),
		"homepage_url": _safe_str(payload.get("HOMEPAGE_URL")),
		"trfc_info": _safe_str(payload.get("TRFC_INFO")),
		"usage_day": usage_day,
		"usage_day_week_and_time": usage_day_week_and_time,
		"usage_amount": _safe_str(payload.get("USAGE_AMOUNT")),
		"main_img_normal": _safe_str(payload.get("MAIN_IMG_NORMAL")),
		"main_img_thumb": _safe_str(payload.get("MAIN_IMG_THUMB")),
		"item_contents": _safe_str(payload.get("ITEMCNTNTS")),
		"middle_size_rm1": _safe_str(payload.get("MIDDLE_SIZE_RM1")),

		# 운영에서 정규화 시킨 축제일정 필드
		"start_date": sch.start_date,
		"end_date": sch.end_date,
		"date_precision": sch.date_precision,
		"extra_schedule_note": sch.extra_schedule_note,  # TextField라 None OK
		"time_info_raw": sch.time_info_raw,
	}


def run_public_festival_apply(
	sync_log: FestivalSyncLog,
	*,
	force: bool = False,
	updated_by: str = "system",
) -> Tuple[int, int, int, int]:

	# apply 시작 기록
	sync_log.apply_status = "RUNNING"
	sync_log.apply_insert_count = 0
	sync_log.apply_update_count = 0
	sync_log.apply_skip_count = 0
	sync_log.apply_error_count = 0
	sync_log.applied_at = None
	sync_log.save(update_fields=[
		"apply_status",
		"apply_insert_count", "apply_update_count", "apply_skip_count", "apply_error_count",
		"applied_at",
	])

	insert_count = 0
	update_count = 0
	skip_count = 0
	error_count = 0

	raws = FestivalRaw.objects.filter(fetched_sync=sync_log).order_by("id")
	now = timezone.now()

	try:
		# 트랜젝션으로 실행
		with transaction.atomic():
			for raw in raws:
				payload = raw.payload or {}
				external_source = raw.external_source
				external_id = raw.external_id
				raw_hash = (raw.payload_hash or "")

				festival = Festival.objects.filter(
					external_source=external_source,
					external_id=external_id,
				).first()

				# 변경 없으면 skip (force면 무시)
				if (not force) and festival is not None:
					if (festival.payload_hash or "") == raw_hash:
						skip_count += 1
						continue

				fields = _map_payload_to_festival_fields(payload)

				if festival is None:
					festival = Festival(
						external_source=external_source,
						external_id=external_id,
					)
					for k, v in fields.items():
						setattr(festival, k, v)

					festival.last_synced_sync = sync_log
					festival.updated_by = updated_by
					festival.payload_hash = raw_hash
					festival.save()
					insert_count += 1

				else:
					for k, v in fields.items():
						setattr(festival, k, v)

					festival.last_synced_sync = sync_log
					festival.updated_by = updated_by
					festival.payload_hash = raw_hash
					festival.updated_at = now
					festival.save()
					update_count += 1

		# 성공 로그
		sync_log.apply_status = "SUCCESS"
		sync_log.apply_insert_count = insert_count
		sync_log.apply_update_count = update_count
		sync_log.apply_skip_count = skip_count
		sync_log.apply_error_count = 0
		sync_log.applied_at = timezone.now()
		sync_log.save(update_fields=[
			"apply_status",
			"apply_insert_count", "apply_update_count", "apply_skip_count", "apply_error_count",
			"applied_at",
		])

		return insert_count, update_count, skip_count, 0

	except Exception as e:
		sync_log.apply_status = "FAIL"
		sync_log.apply_error_count = 1
		sync_log.note = (sync_log.note or "") + f"\n[APPLY FAIL] {type(e).__name__}: {str(e)}"
		sync_log.applied_at = timezone.now()
		sync_log.save(update_fields=["apply_status", "apply_error_count", "note", "applied_at"])
		raise
