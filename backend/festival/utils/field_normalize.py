import re
from typing import Optional

_LANG_TOKENS = {"한", "영", "중간", "중번", "일"}
_PAREN_RE = re.compile(r"\(([^()]*)\)")

def _clean_text(s: Optional[str]) -> str:
  return (s or "").strip()



# 제목에 붙는 (한,영,중간,중번,일) 제거
def normalize_title_display(main_title_raw: Optional[str]) -> Optional[str]:
  s = _clean_text(main_title_raw)
  if not s:
    return None

  def repl(match: re.Match) -> str:
    inside = match.group(1)
    parts = [p.strip() for p in inside.split(",") if p.strip()]
    if parts and all(p in _LANG_TOKENS for p in parts):
        return ""
    return match.group(0)

  cleaned = _PAREN_RE.sub(repl, s)
  cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
  return cleaned or None


## place_display 통일 함수
# place_raw, main_place_raw 둘 다  있으면 place_raw 사용
# place_raw 없으면 main_place_raw 사용
# 둘 다 없으면 None
def normalize_place_display(
  place_raw: Optional[str],
  main_place_raw: Optional[str],
) -> Optional[str]:
  p = (place_raw or "").strip()
  if p:
      return p
  mp = (main_place_raw or "").strip()
  if mp:
      return mp
  return None
