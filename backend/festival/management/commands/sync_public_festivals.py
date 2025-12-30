from django.core.management.base import BaseCommand
from django.utils import timezone

from festival.models import FestivalSyncLog

class Command(BaseCommand):
    help = "공공데이터 축제 정보 동기화 (1단계: 로그만 생성)"

    def handle(self, *args, **options):
        # 1️⃣ RUNNING 로그 생성
        sync_log = FestivalSyncLog.objects.create(
            external_source="PUBLIC_API",
            sync_type=FestivalSyncLog.SyncType.MANUAL,
            status=FestivalSyncLog.Status.RUNNING,
            started_at=timezone.now(),
            triggered_by="system",
        )

        self.stdout.write(
            self.style.WARNING(f"RUNNING 생성됨 (id={sync_log.id})")
        )

        # (여기에 나중에 공공데이터 수집 로직이 들어갈 예정)

        # 2️⃣ SUCCESS로 마감
        sync_log.status = FestivalSyncLog.Status.SUCCESS
        sync_log.finished_at = timezone.now()
        sync_log.result_code = "00"
        sync_log.result_msg = "TEST SUCCESS"
        sync_log.save()

        self.stdout.write(
            self.style.SUCCESS(f"SUCCESS로 종료됨 (id={sync_log.id})")
        )
