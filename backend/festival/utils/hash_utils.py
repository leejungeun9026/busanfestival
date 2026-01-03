import hashlib
from typing import Any, Dict

# None, 숫자, 기타 타입을 문자열로 변환
def _safe_str(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()

# 공공데이터 필드 정규화 + SHA256 해시 생성
def _make_payload_hash(item: Dict[str, Any], core_fields: list[str]) -> str:
    normalized = "|".join(_safe_str(item.get(k)) for k in core_fields)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
