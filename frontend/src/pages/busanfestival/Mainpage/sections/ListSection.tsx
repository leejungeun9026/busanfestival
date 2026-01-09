import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

type SortMode = "date" | "popular";

export type FestivalListItem = {
  festivalId: number | string;
  name?: string;
  period?: string;
  location?: string;
  thumbnailUrl?: string;
  score?: number; // 0~100 (있으면 뱃지/정렬 등에 활용 가능)
};

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-2 text-sm font-semibold" style={{ color: "var(--c-text)" }}>
      {children}
    </h2>
  );
}

function Panel({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-xl p-3"
      style={{
        backgroundColor: "var(--c-surface)",
        border: "1px solid var(--c-border)",
      }}
    >
      {children}
    </div>
  );
}

function SortPill({
  value,
  onChange,
}: {
  value: SortMode;
  onChange: (next: SortMode) => void;
}) {
  return (
    <div
      className="inline-flex items-center gap-1 rounded-lg p-1 text-xs"
      style={{
        backgroundColor: "rgba(184,205,234,0.22)", // soft(alpha)
        border: "1px solid var(--c-border)",
        color: "var(--c-text)",
      }}
    >
      <button
        type="button"
        onClick={() => onChange("date")}
        className="rounded-md px-2 py-1 font-semibold"
        style={{
          backgroundColor: value === "date" ? "rgba(184,205,234,0.55)" : "transparent",
          border: value === "date" ? "1px solid var(--c-border)" : "1px solid transparent",
        }}
      >
        축제일순
      </button>
      <button
        type="button"
        onClick={() => onChange("popular")}
        className="rounded-md px-2 py-1 font-semibold"
        style={{
          backgroundColor: value === "popular" ? "rgba(184,205,234,0.55)" : "transparent",
          border: value === "popular" ? "1px solid var(--c-border)" : "1px solid transparent",
        }}
      >
        인기순
      </button>
    </div>
  );
}

function FestivalCard({
  item,
  onOpenRead,
}: {
  item: FestivalListItem;
  onOpenRead: (festivalId: FestivalListItem["festivalId"]) => void;
}) {
  const name = item.name ?? "(축제명)";
  const period = item.period ?? "(운영기간)";
  const location = item.location ?? "(위치정보)";

  return (
    <article
      className="group overflow-hidden rounded-2xl"
      style={{
        backgroundColor: "var(--c-surface)",
        border: "1px solid var(--c-border)",
        boxShadow: "var(--overlay-shadow)",
      }}
    >
      {/* 3:4 비율 유지 (width:height = 3:4) */}
      <div className="aspect-[3/4]">
        <div className="flex h-full flex-col">
          {/* Thumb 영역 (추후 실제 이미지로 대체) */}
          <div
            className="h-[56%] w-full"
            style={{
              backgroundColor: "var(--c-subtle)",
              borderBottom: "1px solid var(--c-border)",
            }}
          >
            {/* 이미지가 들어올 예정 */}
          </div>

          {/* Content */}
          <div className="flex flex-1 flex-col p-3">
            <div className="min-h-0 flex-1">
              <div
                className="line-clamp-2 text-sm font-semibold"
                style={{ color: "var(--c-text)" }}
                title={name}
              >
                {name}
              </div>
              <div className="mt-1 text-xs" style={{ color: "var(--c-muted)" }}>
                {period}
              </div>
              <div className="mt-1 text-xs" style={{ color: "var(--c-muted)" }}>
                {location}
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between gap-2">
              {typeof item.score === "number" ? (
                <span
                  className="rounded-md px-2 py-1 text-[11px] font-semibold"
                  style={{
                    backgroundColor: "rgba(184,205,234,0.22)",
                    border: "1px solid var(--c-border)",
                    color: "var(--c-text)",
                  }}
                >
                  {Math.round(item.score)}점
                </span>
              ) : (
                <span className="text-[11px]" style={{ color: "var(--c-muted)" }}>
                  {/* score 없으면 표시 생략 */}
                </span>
              )}

              <button
                type="button"
                onClick={() => onOpenRead(item.festivalId)}
                className="rounded-md px-2 py-1 text-[11px] font-semibold"
                style={{
                  backgroundColor: "var(--c-accent)",
                  color: "var(--neutral-0, #fff)",
                }}
              >
                상세보기
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* hover 강조(가벼운 테두리/배경 변화) */}
      <div
        className="pointer-events-none absolute opacity-0 transition-opacity group-hover:opacity-100"
        aria-hidden
      />
    </article>
  );
}

export default function ListSection({ items }: { items?: FestivalListItem[] }) {
  const navigate = useNavigate();
  const [sortMode, setSortMode] = useState<SortMode>("date");

  const mockItems: FestivalListItem[] = useMemo(
    () => [
      { festivalId: 1, name: "부산 불꽃축제", period: "2026-10-01 ~ 2026-10-03", location: "광안리", score: 98 },
      { festivalId: 2, name: "부산 바다축제", period: "2026-08-01 ~ 2026-08-07", location: "해운대", score: 92 },
      { festivalId: 3, name: "부산 국제영화제", period: "2026-10-05 ~ 2026-10-14", location: "영화의전당", score: 90 },
      { festivalId: 4, name: "자갈치 축제", period: "미정", location: "자갈치", score: 86 },
      { festivalId: 5, name: "광안리 해변축제", period: "미정", location: "광안리" },
      { festivalId: 6, name: "해운대 모래축제", period: "미정", location: "해운대" },
    ],
    []
  );

  const list = items ?? mockItems;

  // 정렬은 백엔드 확정 전이므로, 현재는 sortMode UI만 제공하고 데이터는 그대로 둠(추후 교체)
  const onOpenRead = (festivalId: FestivalListItem["festivalId"]) => {
    navigate("/busanfestival/read", { state: { festivalId } });
  };

  return (
    <section>
      <SectionTitle>축제 목록</SectionTitle>
      <Panel>
        <div className="mb-3 flex items-center justify-between gap-2">
          <SortPill value={sortMode} onChange={setSortMode} />
          <div className="text-xs" style={{ color: "var(--c-muted)" }}>
            {list.length}개
          </div>
        </div>

        {/* 
          10.5.3 반영:
          - gap: clamp로 "폭 감소 시 먼저 gap 축소" 구현
          - 컬럼: 3 → 2 → 1 (lg=3, sm=2, base=1)
        */}
        <div
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
          style={{
            gap: "clamp(12px, 2vw, 24px)", // min-gap=12px, max-gap=24px
          }}
        >
          {list.map((item) => (
            <FestivalCard key={String(item.festivalId)} item={item} onOpenRead={onOpenRead} />
          ))}
        </div>
      </Panel>
    </section>
  );
}
