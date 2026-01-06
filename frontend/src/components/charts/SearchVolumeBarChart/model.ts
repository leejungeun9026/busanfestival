import type { FestivalSummary } from "../../overlays/FestivalTooltip/types";

export type SearchVolumeItem = FestivalSummary & {
  searchVolume?: number; // 원시 검색량(있으면 정규화)
  score?: number; // 0~100(백엔드가 정규화해 주는 경우)
};

export type SearchVolumeRow = SearchVolumeItem & {
  normalizedScore: number; // 0~100
};

function clamp0to100(v: number) {
  if (Number.isNaN(v)) return 0;
  return Math.max(0, Math.min(100, v));
}

/**
 * 10.1 규칙:
 * - 상위 5개
 * - 1위 검색량을 100으로 두고 상대 비율 정규화
 * - 백엔드가 score(0~100)를 주면 score 우선 사용
 */
export function normalizeTop5(items: SearchVolumeItem[]): SearchVolumeRow[] {
  if (!items.length) return [];

  const sorted = [...items].sort((a, b) => {
    const av = a.score ?? a.searchVolume ?? 0;
    const bv = b.score ?? b.searchVolume ?? 0;
    return bv - av;
  });

  const top5 = sorted.slice(0, 5);

  const hasAnyScore = top5.some((x) => typeof x.score === "number");
  if (hasAnyScore) {
    return top5.map((x) => ({
      ...x,
      normalizedScore: clamp0to100(x.score ?? 0),
    }));
  }

  const maxVol = Math.max(...top5.map((x) => x.searchVolume ?? 0), 1);
  return top5.map((x) => ({
    ...x,
    normalizedScore: clamp0to100(((x.searchVolume ?? 0) / maxVol) * 100),
  }));
}
