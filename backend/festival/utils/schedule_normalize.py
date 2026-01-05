import re
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Tuple, List


### 결과 DTO ###
@dataclass
class NormalizedSchedule:
  # 정확한 날짜 정보 있는 경우
  start_date: Optional[date]
  end_date: Optional[date]

  # EXACT | RANGE | RANGE_MONTH | RANGE_YEAR | TBD | ALWAYS | UNKNOWN
  date_precision: str

  # 비고 등으로 주는 정보
  extra_schedule_note: Optional[str]

  # 월 정규화(검색용)
  note_months: List[int] = field(default_factory=list)


# =========================
# 전처리 / 파싱 유틸
# =========================

_WEEKDAYS = r"(월|화|수|목|금|토|일)"

def _normalize_base(s: Optional[str]) -> str:
  """모든 파싱/비교 전에 1회만 수행하는 공통 정제"""
  t = (s or "")

  # 보이지 않는 문자 제거
  t = t.replace("\u00A0", " ")   # NBSP
  t = t.replace("\u200B", "")   # ZWSP
  t = t.replace("\u2060", "")   # WORD JOINER
  t = t.replace("\ufeff", "")   # BOM

  # 범위 구분자 통일
  t = t.replace("∼", "~").replace("～", "~").replace("〜", "~")

  # 전각 괄호 → 반각 괄호
  t = t.replace("（", "(").replace("）", ")")

  # 줄바꿈 통일
  t = t.replace("\r\n", "\n").replace("\r", "\n")

  # 양 끝 공백 제거
  t = t.strip()
  return t


def _normalize_for_compare(s: Optional[str]) -> str:
  """비교/분기 판단용 정제"""
  t = _normalize_base(s)
  t = re.sub(r"[ \t]+", " ", t)  # 줄바꿈 제외 공백 압축
  t = t.strip().rstrip(".")      # 끝 점 제거 (2025.07. 같은 케이스)
  return t


def _normalize_for_date_parse(s: str) -> str:
  """날짜/월 파싱용 정제 (요일 제거 포함)"""
  t = _normalize_for_compare(s)

  # (토) 제거
  t = re.sub(rf"\(\s*{_WEEKDAYS}\s*\)", "", t)

  # 날짜 뒤에 붙는 요일 제거: 2024.10.02.수 / 2024-10-02금 / 2024/10/02 토
  t = re.sub(
    rf"((?:20\d{{2}}\s*[.\-/]\s*)?\d{{1,2}}\s*[.\-/]\s*\d{{1,2}}(?:\s*[.\-/]\s*\d{{1,2}})?)\s*\.?\s*{_WEEKDAYS}\b",
    r"\1",
    t
  )

  # 공백 정규화
  t = re.sub(r"\s+", " ", t).strip()
  return t


def _split_extra_note(raw: str) -> Tuple[str, Optional[str]]:
  """
  첫 줄은 날짜/기간 후보, 나머지는 extra_schedule_note로 분리
  예: '2025.5.16 ~ 5.19\n모래조각전 6.8까지 전시'
  """
  raw = _normalize_base(raw)

  lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
  if not lines:
    return "", None

  head = lines[0]
  tail = "\n".join(lines[1:]) if len(lines) > 1 else None

  # 인라인 시간/부가정보 분리 (예: '... 2일 점등시간 : 18:00~24:00')
  for kw in ["점등시간", "운영시간", "관람시간", "시간"]:
    if kw in head:
      before, after = head.split(kw, 1)
      head = before.strip()
      extra = (kw + after).strip()
      tail = (tail + "\n" + extra).strip() if tail else extra
      break

  # '/ ...' 분리
  m = re.search(r"(.*?)(?:\s*/\s*)(.+)$", head)
  if m:
    head = m.group(1).strip()
    extra = m.group(2).strip()
    tail = (tail + "\n" + extra).strip() if tail else extra

  # ', ...' 분리
  m = re.search(r"(.*?),(.*)$", head)
  if m:
    head = m.group(1).strip()
    extra = m.group(2).strip()
    tail = (tail + "\n" + extra).strip() if tail else extra

  return head, (tail or None)


def _extract_year_hint(text: str) -> Optional[int]:
  t = _normalize_for_date_parse(text)
  m = re.search(r"(20\d{2})\s*(?:[.\-/년])", t)
  return int(m.group(1)) if m else None


def _parse_ymd(text: str, year_hint: Optional[int] = None) -> Optional[date]:
  """
  허용 예:
    2025.05.29 / 2025-05-29 / 2025/5/29
    2025년 5월 29일
    5.29 (year_hint 필요)
    5월 29일 (year_hint 필요)
  """
  t = _normalize_for_date_parse(text)

  m = re.search(r"(20\d{2})\s*[.\-/]\s*(\d{1,2})\s*[.\-/]\s*(\d{1,2})", t)
  if m:
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

  m = re.search(r"(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일", t)
  if m:
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

  m = re.search(r"\b(\d{1,2})\s*[.\-/]\s*(\d{1,2})\b", t)
  if m and year_hint:
    return date(year_hint, int(m.group(1)), int(m.group(2)))

  m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", t)
  if m and year_hint:
    return date(year_hint, int(m.group(1)), int(m.group(2)))

  return None


def _parse_ym(text: str, year_hint: Optional[int] = None) -> Optional[Tuple[int, int]]:
  """
  허용 예:
    2025.07 / 2025-7 / 2025/07
    2025년 7월
    7월 (year_hint 필요)
  """
  t = _normalize_for_date_parse(text)

  m = re.search(r"(20\d{2})\s*[.\-/]\s*(\d{1,2})\b", t)
  if m:
    y, mo = int(m.group(1)), int(m.group(2))
    if 1 <= mo <= 12:
      return (y, mo)

  m = re.search(r"(20\d{2})\s*년\s*(\d{1,2})\s*월", t)
  if m:
    y, mo = int(m.group(1)), int(m.group(2))
    if 1 <= mo <= 12:
      return (y, mo)

  m = re.search(r"(\d{1,2})\s*월", t)
  if m and year_hint:
    mo = int(m.group(1))
    if 1 <= mo <= 12:
      return (year_hint, mo)

  return None


# =========================
# 월 추출 유틸
# =========================

def _dedup_sorted_months(months: List[int]) -> List[int]:
  return sorted({x for x in months if 1 <= x <= 12})


def _month_range(start_m: int, end_m: int) -> List[int]:
  """
  5~10 -> [5,6,7,8,9,10]
  11~2 -> [11,12,1,2]  (연말跨年)
  """
  if not (1 <= start_m <= 12 and 1 <= end_m <= 12):
    return []
  if start_m <= end_m:
    return list(range(start_m, end_m + 1))
  return list(range(start_m, 13)) + list(range(1, end_m + 1))


def _extract_months_any(text: Optional[str]) -> List[int]:
  """
  텍스트에서 월 정보만 최대한 뽑아냄.
  - 11월
  - 2025년 7월
  - 2025.07 / 2025-7 / 2025/07
  """
  if not text:
    return []

  t = _normalize_for_compare(text)
  months: List[int] = []

  # n월
  for m in re.finditer(r"\b(1[0-2]|[1-9])\s*월\b", t):
    months.append(int(m.group(1)))

  # YYYY년 n월
  for m in re.finditer(r"(20\d{2})\s*년\s*(1[0-2]|[1-9])\s*월", t):
    months.append(int(m.group(2)))

  # YYYY.07 / YYYY-7 / YYYY/07
  for m in re.finditer(r"(20\d{2})\s*[.\-/]\s*(1[0-2]|0?[1-9])\b", t):
    months.append(int(m.group(2)))

  return _dedup_sorted_months(months)


def _extract_note_months(raw: str, extra_note: Optional[str]) -> List[int]:
  months = _extract_months_any(raw) + _extract_months_any(extra_note)
  return _dedup_sorted_months(months)


def _extract_note_months_enhanced(text: str, extra_note: Optional[str]) -> List[int]:
  """
  raw(헤드) + extra_note에서 월 정보를 뽑아 note_months로 만든다.
  - 8월 같은 단일 월
  - 5월~10월 같은 월 범위는 [5..10] 확장
  - 2025.07 ~ 2025.10 같은 연-월 범위도 [7..10] 확장
  - '6. 11' 같은 월-일 패턴이 있으면 월(6)도 뽑아준다 (연도 없어도 month 검색 가능하게)
  """
  base = _normalize_for_compare(text)
  tail = _normalize_for_compare(extra_note) if extra_note else ""
  joined = (base + " " + tail).strip()

  months: List[int] = []

  # (A) 기존 단일 월 추출(8월, 2025년 8월, 2025.08 등)
  months += _extract_months_any(joined)

  # (B) '5월~10월' 범위 확장
  m = re.search(r"(1[0-2]|[1-9])\s*월\s*[~\-]\s*(1[0-2]|[1-9])\s*월", joined)
  if m:
    months += _month_range(int(m.group(1)), int(m.group(2)))

  # (C) '2025.07 ~ 2025.10' 또는 '2025-07 ~ 2025-10' 같은 연-월 범위 확장
  if "~" in joined:
    left, right = [p.strip() for p in joined.split("~", 1)]
    y1m1 = _parse_ym(left)
    y2m2 = _parse_ym(right)
    if y1m1 and y2m2:
      y1, m1 = y1m1
      y2, m2 = y2m2
      if y1 == y2:
        months += _month_range(m1, m2)
      else:
        months += list(range(m1, 13)) + list(range(1, m2 + 1))

  # (D) 연도 없는 '6.11', '6/11', '6-11' 같은 월-일 패턴에서도 월을 뽑아줌
  for mm in re.finditer(r"\b(1[0-2]|[1-9])\s*[.\-/]\s*(\d{1,2})\b", joined):
    months.append(int(mm.group(1)))

  return _dedup_sorted_months(months)



# =========================
# 동일 필드 비교
# =========================

def _is_same_schedule(u1: Optional[str], u2: Optional[str]) -> bool:
  a = _normalize_for_compare(u1)
  b = _normalize_for_compare(u2)
  return bool(a) and bool(b) and a == b


# =========================
# 메인 정규화 함수
# =========================

def normalize_schedule(
  usage_day: Optional[str],
  usage_day_week_and_time: Optional[str],
) -> NormalizedSchedule:

  # 0) 비교용 정규화(공백/범위기호/끝점 등)
  u1 = _normalize_for_compare(usage_day)
  u2 = _normalize_for_compare(usage_day_week_and_time)

  # 1) 같은 내용이면 하나로 통합
  if _is_same_schedule(u1, u2):
    candidate_source = u1 or ""
  else:
    candidate_source = (u2 or u1) or ""

  # 2) 파싱 대상(첫 줄)과 부가 노트 분리
  candidate, extra_note = _split_extra_note(candidate_source)
  raw = _normalize_for_compare(candidate)

  # 기본값 (EXACT/RANGE에서는 비움)
  note_months: List[int] = []

  # 1) 상시/연중/항시 → ALWAYS
  if re.search(r"(상시|연중|항시)", raw):
    return NormalizedSchedule(
      start_date=None,
      end_date=None,
      date_precision="ALWAYS",
      extra_schedule_note=(extra_note or raw or None),
      note_months=[]
    )

  # 2) 추후/미정/예정 → TBD
  if re.search(r"(추후|미정|예정)", raw):
    note_months = _extract_note_months_enhanced(raw, extra_note)
    return NormalizedSchedule(
      start_date=None,
      end_date=None,
      date_precision="TBD",
      extra_schedule_note=(extra_note or raw or None),
      note_months=note_months
    )

  # 3) 매년 반복 → RANGE_YEAR
  # 요구사항 기준: note_months 비움 (원하면 아래 주석 해제)
  if re.search(r"매년", raw):
    note_months = _extract_note_months_enhanced(raw, extra_note) 
    return NormalizedSchedule(
      start_date=None,
      end_date=None,
      date_precision="RANGE_YEAR",
      extra_schedule_note=(extra_note or raw or None),
      note_months=note_months
    )

  # 4) 월 범위 (예: 5월~10월) → RANGE_MONTH (✅ note_months 채움)
  m = re.search(r"(1[0-2]|[1-9])\s*월\s*[~\-]\s*(1[0-2]|[1-9])\s*월", raw)
  if m:
    start_m = int(m.group(1))
    end_m = int(m.group(2))
    note_months = _month_range(start_m, end_m)

    return NormalizedSchedule(
      start_date=None,
      end_date=None,
      date_precision="RANGE_MONTH",
      extra_schedule_note=(extra_note or raw or None),
      note_months=note_months
    )

  # 5) 날짜/월 범위(~ 포함)
  if "~" in raw:
    left, right = [p.strip() for p in raw.split("~", 1)]

    # year_hint: 왼쪽에 있으면 우선, 없으면 전체에서 추출
    year_hint = _extract_year_hint(left) or _extract_year_hint(raw)

    start_ymd = _parse_ymd(left, year_hint=year_hint)
    end_ymd = _parse_ymd(right, year_hint=year_hint)

    # 5-1) YYYY.MM.DD ~ YYYY.MM.DD → RANGE
    if start_ymd and end_ymd:
      return NormalizedSchedule(
        start_date=start_ymd,
        end_date=end_ymd,
        date_precision="RANGE",
        extra_schedule_note=extra_note,
        note_months=[]
      )

    # 5-2) YYYY.MM ~ YYYY.MM → RANGE_MONTH
    ym_start = _parse_ym(left, year_hint=year_hint)
    ym_end = _parse_ym(right, year_hint=year_hint)
    if ym_start and ym_end:
      y1, m1 = ym_start
      y2, m2 = ym_end

      # 검색용 month만 필요
      if y1 == y2:
        note_months = _month_range(m1, m2)
      else:
        note_months = list(range(m1, 13)) + list(range(1, m2 + 1))

      note_months = _dedup_sorted_months(note_months)

      return NormalizedSchedule(
        start_date=None,
        end_date=None,
        date_precision="RANGE_MONTH",
        extra_schedule_note=(extra_note or raw or None),
        note_months=note_months
      )

    # 5-3) 범위인데 파싱 실패 → UNKNOWN
    return NormalizedSchedule(
      start_date=None,
      end_date=None,
      date_precision="UNKNOWN",
      extra_schedule_note=(extra_note or raw or None),
      note_months=[]
    )

  # 6) 단일 날짜 → EXACT
  year_hint = _extract_year_hint(raw)
  single = _parse_ymd(raw, year_hint=year_hint)
  if single:
    return NormalizedSchedule(
      start_date=single,
      end_date=single,
      date_precision="EXACT",
      extra_schedule_note=extra_note,
      note_months=[]
    )

  # 7) 전부 실패 → UNKNOWN
  fallback_note = extra_note or raw or None
  unknown_months = _extract_months_any(candidate_source)

  return NormalizedSchedule(
    start_date=None,
    end_date=None,
    date_precision="UNKNOWN",
    extra_schedule_note=fallback_note,
    note_months=unknown_months
  )
