from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from festival.models import Festival, FestivalRaw, FestivalSyncLog
from festival.utils.schedule_normalize import normalize_schedule
from festival.utils.field_normalize import normalize_title_display, normalize_place_display


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
def _map_payload_to_festival_fields(
	payload: Dict[str, Any],
	*,
	include_display_fields: bool = True,
) -> Dict[str, Any]:
	usage_day = _safe_str(payload.get("USAGE_DAY"))
	usage_day_week_and_time = _safe_str(payload.get("USAGE_DAY_WEEK_AND_TIME"))

	sch = normalize_schedule(
		usage_day=usage_day,
		usage_day_week_and_time=usage_day_week_and_time,
	)

	main_title_raw = _safe_str(payload.get("MAIN_TITLE"))
	main_place_raw = _safe_str(payload.get("MAIN_PLACE"))
	place_raw = _safe_str(payload.get("PLACE"))

	data = {
		# 공공데이터 필드 매핑
		"main_title_raw": main_title_raw,
		"main_place_raw": main_place_raw,
		"place_raw": place_raw,

		"gugun_nm": _safe_str(payload.get("GUGUN_NM")),
		"lat": _safe_decimal(payload.get("LAT")),
		"lng": _safe_decimal(payload.get("LNG")),

		"title": _safe_str(payload.get("TITLE")),
		"subtitle": _safe_str(payload.get("SUBTITLE")),
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
		"facilities": _safe_str(payload.get("MIDDLE_SIZE_RM1")),

		# 정규화 시킨 축제일정 필드
		"start_date": sch.start_date,
		"end_date": sch.end_date,
		"date_precision": sch.date_precision,
		"extra_schedule_note": sch.extra_schedule_note,  # TextField라 None OK
		"note_months": sch.note_months
	}

	# 정규화시킨 title, place
	# 관리자가 수정했으면 덮어씌우지 않도록 따로 관리
	if include_display_fields:
		data["main_title_display"] = normalize_title_display(main_title_raw)
		data["place_display"] = normalize_place_display(place_raw, main_place_raw)

	return data


PROTECTED_FIELDS = {"main_title_display", "place_display"}

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

				# 1) 변경 없으면 skip (force면 무시)
				if (not force) and festival is not None:
					if (festival.payload_hash or "") == raw_hash:
						skip_count += 1
						continue
				
				# 2) 신규 생성은 무조건 display 세팅 포함
				if festival is None:
					fields = _map_payload_to_festival_fields(payload)

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

				# 3) 기존 데이터 업데이트
				edited = set(festival.edited_fields or [])
				# force면 보호필드도 덮어쓰기 허용
				allow_override_display = force or len(PROTECTED_FIELDS & edited) == 0

				fields = _map_payload_to_festival_fields(
					payload,
					include_display_fields=allow_override_display,
				)

				if force:
    			# force면 보호필드의 운영자 수정 흔적 제거 (시스템 관리로 전환)
					if festival.edited_fields:
						festival.edited_fields = [f for f in festival.edited_fields if f not in PROTECTED_FIELDS]
				else:
						# 운영자가 수정한 보호필드는 덮어쓰지 않음 (필드 단위)
					for f in PROTECTED_FIELDS:
						if f in edited:
							fields.pop(f, None)

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
