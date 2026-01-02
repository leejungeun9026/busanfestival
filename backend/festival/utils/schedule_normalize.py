import re
from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple



### 결과 DTO ###
@dataclass
class NormalizedSchedule:
  # 정확한 날자 정보 있는 경우
  start_date: Optional[date]
  end_date: Optional[date]

  # EXACT | RANGE | RANGE_MONTH | RANGE_YEAR | TBD | ALWAYS | UNKNOWN
  date_precision: str  

  # 비고 등으로 주는 정보
  extra_schedule_note: Optional[str]

  # 축제 시간 정보 원문
  time_info_raw: Optional[str]

  # 원본값
  raw_merged: str


### 전처리 함수 ###
# None-safe 문자열 정리
def _clean_text(s: Optional[str]) -> str:
  # NBSP, ZWSP 같은 보이지 않는 공백/문자 제거 + 공백 정규화
  t = (s or "")
  t = t.replace("\u00A0", " ")   # NBSP
  t = t.replace("\u200B", "")   # ZWSP
  t = t.replace("\u2060", "")   # WORD JOINER
  t = t.replace("\ufeff", "")   # BOM
  t = t.strip()
  t = re.sub(r"\s+", " ", t)
  return t

def _normalize_separators(s: str) -> str:
  # ∼, ～ 같은 범위 기호를 ~ 로 통일 + 전각 물결 등 정리
  return s.replace("∼", "~").replace("～", "~").replace("〜", "~")

def _strip_trailing_dots(s: str) -> str:
  # '2025.07.' 처럼 끝에 점이 붙는 케이스 정리
  return s.strip().rstrip(".")

# "(월)" 같은 요일 제거
def _remove_weekday(text: str) -> str:
  # 전각 괄호도 같이 처리
  t = text.replace("（", "(").replace("）", ")")

  # (토) / ( 토 ) 형태 제거
  t = re.sub(r"\(\s*(월|화|수|목|금|토|일)\s*\)", "", t)

  # 2024.10.02.수 / 2024-10-02금 / 2024/10/02 토 처럼 날짜 뒤에 붙은 요일 제거
  # look-behind 없이: (날짜패턴)(요일)로 잡아서 날짜만 남김
  t = re.sub(
    r"((?:20\d{2}\s*[.\-/]\s*)?\d{1,2}\s*[.\-/]\s*\d{1,2}(?:\s*[.\-/]\s*\d{1,2})?)\s*\.?\s*(월|화|수|목|금|토|일)\b",
    r"\1",
    t
  )

  return t

# 년도 추출(기간 중 끝나는 날짜에 년도 없는 경우 사용하기 위해)
def _extract_year_hint(text: str) -> Optional[int]:
  m = re.search(r"(20\d{2})\s*(?:[.\-/년])", text)
  return int(m.group(1)) if m else None

# 줄바꿈 기준으로 첫 줄: 날짜 후보, 나머지: extra_schedule_note
def _split_extra_note(raw: str) -> Tuple[str, Optional[str]]:
  """
  '...\n모래조각전 6.8.(일)까지 전시' 같은 경우
  첫 줄은 기간 후보, 나머지는 extra_note로 분리
  """
  raw = _clean_text(raw)
  raw = _normalize_separators(raw)

  lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
  if not lines:
    return "", None
  if len(lines) == 1:
    head, tail = lines[0], None
  else:
    head, tail = lines[0], "\n".join(lines[1:])

  # 인라인으로 붙는 시간/부가정보 분리 (예: '... 2일 점등시간 : 18:00~24:00')
  for kw in ["점등시간", "운영시간", "관람시간", "시간"]:
    if kw in head:
      before, after = head.split(kw, 1)
      before = before.strip()
      extra = (kw + after).strip()
      tail = (tail + "\n" + extra).strip() if tail else extra
      head = before
      break

  # '/ 2일간', '/ 상시운영' 같은 부가정보 분리
  m = re.search(r"(.*?)(?:\s*/\s*)(.+)$", head)
  if m:
    head = m.group(1).strip()
    extra = m.group(2).strip()
    tail = (tail + "\n" + extra).strip() if tail else extra

  # ', 매주 ...' 같은 부가정보 분리
  m = re.search(r"(.*?),(.*)$", head)
  if m:
    head = m.group(1).strip()
    extra = m.group(2).strip()
    tail = (tail + "\n" + extra).strip() if tail else extra

  return head, (tail or None)



### 날짜 파싱 함수 ###
def _parse_ymd(text: str, year_hint: Optional[int] = None) -> Optional[date]:
  """
  허용 형태 예:
    2025.05.29
    2025-05-29
    2025/5/29
    5.29  (year_hint가 있으면 사용)
  """

  t = _strip_trailing_dots(_remove_weekday(text))
  t = _clean_text(t)

  # 연-월-일 완전한 경우
  m = re.search(r"(20\d{2})\s*[.\-/]\s*(\d{1,2})\s*[.\-/]\s*(\d{1,2})", t)
  if m:
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

  # '2025년 5월 29일'
  m = re.search(r"(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일", t)
  if m:
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

  # 월-일만 있는 경우 → year_hint 필요
  m = re.search(r"\b(\d{1,2})\s*[.\-/]\s*(\d{1,2})\b", t)
  if m and year_hint:
    return date(year_hint, int(m.group(1)), int(m.group(2)))

  # 5월 29일
  m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", t)
  if m and year_hint:
    return date(year_hint, int(m.group(1)), int(m.group(2)))

  return None

def _parse_ym(text: str, year_hint: Optional[int] = None) -> Optional[Tuple[int, int]]:
  t = _strip_trailing_dots(_remove_weekday(text))
  t = _clean_text(t)

  # 2025.07 / 2025-7 / 2025/07
  m = re.search(r"(20\d{2})\s*[.\-/]\s*(\d{1,2})\b", t)
  if m:
    y, mo = int(m.group(1)), int(m.group(2))
    if 1 <= mo <= 12:
      return (y, mo)

  # 2025년 7월
  m = re.search(r"(20\d{2})\s*년\s*(\d{1,2})\s*월", t)
  if m:
    y, mo = int(m.group(1)), int(m.group(2))
    if 1 <= mo <= 12:
      return (y, mo)

  # 월만 있는 경우 → year_hint 필요
  m = re.search(r"(\d{1,2})\s*월", t)
  if m and year_hint:
    mo = int(m.group(1))
    if 1 <= mo <= 12:
      return (year_hint, mo)

  return None



### 메인 정규화 함수 ###
def normalize_schedule(
  usage_day: Optional[str], 
  usage_day_week_and_time: Optional[str]
) -> NormalizedSchedule:
  
  u1 = _clean_text(usage_day)
  u2 = _clean_text(usage_day_week_and_time)

  # 원본 보존
  raw_merged = " | ".join([x for x in [u1, u2] if x])

  # 시간/요일 정보는 보통 usage_day_week_and_time 쪽이 더 정확
  time_info_raw = u2 or None

  # 우선순위 : 실제 날짜가 들어있는 쪽을 먼저 파싱
  candidate, extra_note = _split_extra_note(u2 or u1)

  raw = candidate or u1 or u2
  raw = _clean_text(raw)
  raw = _normalize_separators(raw)

  # 1) 상시/연중/항상
  if re.search(r"(상시|연중|항시)", raw):
    return NormalizedSchedule(
      None, None, "ALWAYS",
      extra_note or raw, time_info_raw, raw_merged
    )

  # 2) 추후 공지
  if re.search(r"(추후|미정|예정)", raw):
    return NormalizedSchedule(
      None, None, "TBD",
      extra_note or raw, time_info_raw, raw_merged
    )

  # 3) 매년 반복
  if re.search(r"매년", raw):
    return NormalizedSchedule(
      None, None, "RANGE_YEAR",
      extra_note or raw, time_info_raw, raw_merged
    )

  # 4) 월 범위 (2025년 5월~10월)
  if re.search(r"\d{1,2}\s*월\s*[~\-]\s*\d{1,2}\s*월", raw):
    return NormalizedSchedule(
      None, None, "RANGE_MONTH",
      extra_note or raw, time_info_raw, raw_merged
    )
  
  # 5) 날짜 범위
  if "~" in raw:
    left, right = [p.strip() for p in raw.split("~", 1)]
    left = _clean_text(left)
    right = _clean_text(right)

    year_hint = _extract_year_hint(left) or _extract_year_hint(raw)

    start_ymd = _parse_ymd(left, year_hint=year_hint)
    end_ymd = _parse_ymd(right, year_hint=year_hint)

    if start_ymd and end_ymd:
      return NormalizedSchedule(
        start_ymd, end_ymd, "RANGE",
        extra_note, time_info_raw, raw_merged
      )

    ym_start = _parse_ym(left, year_hint=year_hint)
    ym_end = _parse_ym(right, year_hint=year_hint)

    if ym_start and ym_end:
      return NormalizedSchedule(
        None, None, "RANGE_MONTH",
        extra_note or raw, time_info_raw, raw_merged
      )

    # 파싱 실패 시 UNKNOWN, raw를 extra_note로 남김
    return NormalizedSchedule(
      None, None, "UNKNOWN",
      extra_note or raw, time_info_raw, raw_merged
    )

  # 6) 단일 날짜: 2025.11.15.(토)
  year_hint = _extract_year_hint(raw)
  single = _parse_ymd(raw, year_hint=year_hint)

  if single:
    return NormalizedSchedule(
      single, single, "EXACT",
      extra_note, time_info_raw, raw_merged
    )

  # 7) 전부 실패 : 알 수 없음
  return NormalizedSchedule(
    None, None, "UNKNOWN",
    extra_note or raw or None,
    time_info_raw,
    raw_merged
  )
