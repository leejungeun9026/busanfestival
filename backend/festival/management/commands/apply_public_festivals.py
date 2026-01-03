from django.core.management.base import BaseCommand, CommandError

from festival.models import FestivalSyncLog
from festival.services.public_festival_apply import run_public_festival_apply


class Command(BaseCommand):
	help = "FestivalRaw(원본) -> Festival(운영) 반영 (sync_log_id 기준)"

	def add_arguments(self, parser):
		parser.add_argument(
			"--sync-log-id",
			type=int,
			required=True,
			help="반영할 FestivalSyncLog id",
		)
		parser.add_argument(
			"--force",
			action="store_true",
			help="skip 최적화 무시하고 무조건 update/insert 수행",
		)

	def handle(self, *args, **options):
		sync_log_id = options["sync_log_id"]
		force = options["force"]

		sync_log = FestivalSyncLog.objects.filter(id=sync_log_id).first()
		if not sync_log:
			raise CommandError(f"FestivalSyncLog not found. id={sync_log_id}")

		self.stdout.write(self.style.WARNING(
			f"운영 반영 시작 (sync_log_id={sync_log.id}, "
			f"sync_status={sync_log.status}, apply_status=RUNNING, force={force})"
		))

		insert_count, update_count, skip_count, error_count = run_public_festival_apply(
			sync_log,
			force=force,
			updated_by="system",
		)

		self.stdout.write(self.style.SUCCESS(
			f"운영 반영 완료 (sync_log_id={sync_log.id}, "
			f"apply_insert={insert_count}, apply_update={update_count}, apply_skip={skip_count}, apply_error={error_count})"
		))
