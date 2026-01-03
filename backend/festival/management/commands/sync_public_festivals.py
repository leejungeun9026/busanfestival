from django.core.management.base import BaseCommand

from festival.models import FestivalSyncLog
from festival.services.public_festival_sync import run_public_festival_sync

class Command(BaseCommand):
    help = "공공데이터 축제 정보 동기화"

    def handle(self, *args, **options):
        # RUNNING 로그 생성
        sync_log = FestivalSyncLog.objects.create(
            external_source="PUBLIC_API",
            sync_type=FestivalSyncLog.SyncType.MANUAL,
            status=FestivalSyncLog.Status.RUNNING,
            triggered_by="system",
        )

        self.stdout.write(
            self.style.WARNING(f"RUNNING 생성됨 (id={sync_log.id})")
        )

        # API 동기화 실행
        try:
            run_public_festival_sync(sync_log, page_size=100)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"동기화 실패 (id={sync_log.id}): {e}"))
            raise

        # 결과 출력 (DB에서 최신값 다시 읽는 게 안전)
        sync_log.refresh_from_db()
        self.stdout.write(
            self.style.SUCCESS(
                f"동기화 종료 (id={sync_log.id}, status={sync_log.status}, "
                f"insert={sync_log.insert_count}, update={sync_log.update_count}, "
                f"skip={sync_log.skip_count}, error={sync_log.error_count}, "
                f"raw={sync_log.raw_file_path})"
            )
        )
