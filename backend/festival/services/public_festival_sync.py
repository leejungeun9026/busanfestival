import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from typing import Any, Dict, List, Tuple

from festival.models import FestivalRaw, FestivalSyncLog
from festival.utils.hash_utils import _make_payload_hash
from festival.utils.raw_snapshot_utils import save_public_festival_snapshot_json

# 공공데이터 API URL
API_URL = "http://apis.data.go.kr/6260000/FestivalService/getFestivalKr"

ENDPOINT_KEY = "getFestivalKr"

# payload_hash용 필드
# 이 필드 내용 변경되면 공공데이터 변경된 것으로 판단
CORE_FIELDS = [
	"UC_SEQ",
	"MAIN_TITLE",
	"GUGUN_NM",
	"LAT",
	"LNG",
	"PLACE",
	"TITLE",
	"SUBTITLE",
	"MAIN_PLACE",
	"ADDR1",
	"ADDR2",
	"CNTCT_TEL",
	"HOMEPAGE_URL",
	"TRFC_INFO",
	"USAGE_DAY",
	"USAGE_DAY_WEEK_AND_TIME",
	"USAGE_AMOUNT",
	"MAIN_IMG_NORMAL",
	"MAIN_IMG_THUMB",
	"ITEMCNTNTS",
	"MIDDLE_SIZE_RM1",
]


# 공공데이터 API 호출 함수 생성
def _fetch_page(page_no: int, num_of_rows: int) -> Tuple[List[Dict[str, Any]], int, str, str]:

	# 서비스 키
	service_key = getattr(settings, "PUBLIC_DATA_SERVICE_KEY", "")
	if not service_key:
		raise RuntimeError("PUBLIC_DATA_SERVICE_KEY가 설정되어 있지 않아요.")

	# API 요청 파라미터 구성
	params = {
		"serviceKey": service_key,
		"pageNo": page_no,
		"numOfRows": num_of_rows,
		"resultType": "json",
	}

	# HTTP 요청 및 응답 저장
	res = requests.get(API_URL, params=params, timeout=20)
	res.raise_for_status()
	data = res.json()

	root = data.get(ENDPOINT_KEY) or {}
	header = root.get("header") or {}

	code = str(header.get("code", "")).strip()
	msg = str(header.get("message", "")).strip()

	# 예외처리, 응답 코드가 있고 00이 아닐 때
	if code and code != "00":
		raise RuntimeError(f"공공데이터 응답 오류: code={code}, message={msg or 'UNKNOWN'}")

	# items리스트 가져오기
	items = root.get("item") or []

	# totalCount는 표준 응답이면 body.totalCount에 있을 수 있어서 둘 다 시도
	total_count_raw = (root.get("totalCount")
										 	or (root.get("body")
											or {}).get("totalCount")
											or len(items))

	try:
			total_count = int(total_count_raw)
	except (TypeError, ValueError):
			total_count = len(items)

	return items, total_count, (code or ""), (msg or "")



### 페이지 순회하며 DB에 upsert ###
def run_public_festival_sync(sync_log: FestivalSyncLog, page_size: int = 100) -> None:

	# 요청 시작 시간
	started_at = timezone.now()

	# sync_log 초기 상태인  RUNNING(동기화 진행 중) 저장
	sync_log.started_at = started_at
	sync_log.status = FestivalSyncLog.Status.RUNNING
	sync_log.request_rows = page_size
	sync_log.save(update_fields=["started_at", "status", "request_rows"])

	# 통계 카운터
	insert_count = 0
	update_count = 0
	skip_count = 0
	error_count = 0

	last_total_count = None
	last_code = ""
	last_msg = ""

	# 원본 저장용 배열 생성
	all_items: List[Dict[str, Any]] = []

	# 페이지 1부터 순회 시작
	page_no = 1
	try:
		while True:
			items, total_count, code, msg = _fetch_page(page_no=page_no, num_of_rows=page_size)

			last_total_count, last_code, last_msg = total_count, code, msg

			if not items:
				break

			# JSON 파일 저장 위해 리스트에 추가
			all_items.extend(items)

			# DB 저장 작업
			# 아래 작업을 transaction으로 처리
			with transaction.atomic():
				for item in items:
					# 고유 아이디 가져오기
					uc_seq = item.get("UC_SEQ")
					# 고유 아이디 없으면 실패 항목에 저장
					if not uc_seq:
						error_count += 1
						continue

					external_id = str(uc_seq).strip()

					# CORE_FIELDS만 정규화해서 해시 생성
					payload_hash = _make_payload_hash(item, CORE_FIELDS)

					# festival_raw에서 중복/갱신 판단을 위한 조회 조건
					lookup = { "external_source": sync_log.external_source,  "external_id": external_id,}

					# 기존에 동일한 축제가 저장되어 있는지 확인
					obj = FestivalRaw.objects.filter(**lookup).first()

					# 신규 데이터라면 insert
					if obj is None:
						FestivalRaw.objects.create(
							**lookup,
							payload=item,
							payload_hash=payload_hash,
							fetched_sync=sync_log,
							last_synced_at=timezone.now(),
						)
						insert_count += 1

					# 기존 데이터라면 update or skip
					else:
						# 저장된 해시와 신규 해시 비교
						if (obj.payload_hash or "") == payload_hash:
							skip_count += 1
							continue
						# 변경된 내용있으면 최신값 저장
						obj.payload = item
						obj.payload_hash = payload_hash
						obj.fetched_sync = sync_log
						obj.last_synced_at = timezone.now()
						obj.save(update_fields=["payload", "payload_hash", "fetched_sync", "last_synced_at", "updated_at"])
						update_count += 1
			page_no += 1	# 다음 페이지 이동


		# 원본 JSON파일 저장
		raw_path, raw_size, raw_checksum = save_public_festival_snapshot_json(
			items=all_items,
			source=sync_log.external_source,
			endpoint_key=ENDPOINT_KEY,
			filename_prefix="festival",
		)

		sync_log.raw_file_path = raw_path
		sync_log.raw_file_size = raw_size
		sync_log.raw_file_checksum = raw_checksum

		# 성공 마감
		sync_log.status = FestivalSyncLog.Status.SUCCESS
		sync_log.finished_at = timezone.now()
		sync_log.result_code = last_code or "00"
		sync_log.result_msg = last_msg or "NORMAL_CODE"
		sync_log.total_count = last_total_count
		sync_log.insert_count = insert_count
		sync_log.update_count = update_count
		sync_log.skip_count = skip_count
		sync_log.error_count = error_count
		sync_log.save()

	except Exception as e:
		# 실패 마감
		sync_log.status = FestivalSyncLog.Status.FAIL
		sync_log.finished_at = timezone.now()
		sync_log.result_code = sync_log.result_code or "99"
		sync_log.result_msg = str(e)[:255]
		sync_log.error_count = (sync_log.error_count or 0) + 1
		sync_log.note = (sync_log.note or "") + f"\n{str(e)}"
		sync_log.save()
		raise
