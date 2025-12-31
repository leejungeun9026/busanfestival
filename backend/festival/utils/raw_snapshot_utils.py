import json
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from django.conf import settings
from django.utils import timezone


def _sha256_bytes(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


# json 파일 저장용 함수
def save_public_festival_snapshot_json(
  *,
  items: List[Dict[str, Any]],
  source: str = "PUBLIC_API",
  endpoint_key: str = "getFestivalKr",
  filename_prefix: str = "festival",
  base_dir: Optional[Path] = None,
) -> Tuple[str, int, str]:
  
  # static 디렉토리 기준 경로
  static_root = Path(getattr(settings, "BASE_DIR", Path.cwd())) / "static"
  if base_dir is None:
    base_dir = static_root / "data" / "festival"

  base_dir.mkdir(parents=True, exist_ok=True)

  ts = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M%S")
  filename = f"{filename_prefix}_{ts}.json"
  abs_path = base_dir / filename

  payload = {
    "meta": {
      "source": source,
      "endpoint_key": endpoint_key,
      "saved_at": timezone.localtime(timezone.now()).isoformat(),
      "items_count": len(items),
    },
    "items": items,
  }

  # json bytes 생성 (checksum/size 계산용)
  raw_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

  # 파일 저장
  abs_path.write_bytes(raw_bytes)

  # 파일 메타
  size = abs_path.stat().st_size
  checksum = _sha256_bytes(raw_bytes)

  # static 하위 상대경로로 저장
  rel_path = abs_path.relative_to(static_root).as_posix()

  return rel_path, size, checksum
