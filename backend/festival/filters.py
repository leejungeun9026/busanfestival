import django_filters
from django.db.models import Q
from django.db.models.functions import ExtractMonth
from django.db.models import F

from .models import Festival


class FestivalFilter(django_filters.FilterSet):
  month = django_filters.NumberFilter(method="filter_month")

  def filter_month(self, queryset, name, value):
    if value in (None, ""):
      return queryset

    try:
        month = int(value)
    except (TypeError, ValueError):
      return queryset

    if not (1 <= month <= 12):
      return queryset

    # 1) 날짜 있는 데이터: start/end 월 겹침 판정
    dated = queryset.filter(start_date__isnull=False).annotate(
      start_m=ExtractMonth("start_date"),
      end_m=ExtractMonth("end_date"),
    )

    # 같은 해 안에서 끝나는 경우 (ex: 5~8)
    q_same_year = Q(start_m__lte=F("end_m")) & Q(start_m__lte=month, end_m__gte=month)

    # 연도 넘어가는 경우 (ex: 10~1)
    q_cross_year = Q(start_m__gt=F("end_m")) & (Q(start_m__lte=month) | Q(end_m__gte=month))

    dated_ids = dated.filter(q_same_year | q_cross_year).values_list("id", flat=True)

    # 2) 날짜 없는 데이터: note_months 포함 여부 (둘 다 NULL인 케이스)
    q_note = Q(start_date__isnull=True, end_date__isnull=True) & Q(note_months__contains=[month])

    # 최종: 날짜기반 매칭 + note 기반 매칭
    return queryset.filter(Q(id__in=dated_ids) | q_note)

  class Meta:
    model = Festival
    fields = ["gugun_nm", "month"]
