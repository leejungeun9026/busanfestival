import { useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Header, { type NavbarSearchParams } from "../../../components/layout/Header/Header";
import { SearchVolumeBarChart, mockSearchVolumeTop5 } from "../../../components/charts/SearchVolumeBarChart";
import { FestivalTooltip, type FestivalSummary } from "../../../components/overlays/FestivalTooltip";
import type { SearchVolumeRow } from "../../../components/charts/SearchVolumeBarChart";
import MapSection from "./sections/MapSection";

type LocationState = {
  searchParams?: Partial<NavbarSearchParams>;
};

type FestivalListItem = {
  festivalId: number | string;
  name?: string;
  period?: string;
  location?: string;
  score?: number; // 임시/선택: 0~100
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
          {/* Thumb 영역(추후 이미지로 교체) */}
          <div
            className="h-[56%] w-full"
            style={{
              backgroundColor: "var(--c-subtle)",
              borderBottom: "1px solid var(--c-border)",
            }}
          />

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
                <span className="text-[11px]" style={{ color: "var(--c-muted)" }} />
              )}

              <button
                type="button"
                onClick={() => onOpenRead(item.festivalId)}
                className="rounded-md px-2 py-1 text-[11px] font-semibold"
                style={{
                  backgroundColor: "var(--c-accent)",
                  color: "var(--neutral-0)",
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--c-hover)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.backgroundColor = "var(--c-accent)";
                }}
              >
                상세보기
              </button>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

export default function MainPage() {
  const navigate = useNavigate();

  // Header search params(기존 유지)
  const location = useLocation();
  const state = (location.state ?? {}) as LocationState;

  const initialSearch = useMemo(
    () => ({
      period: state.searchParams?.period ?? "",
      region: state.searchParams?.region ?? "",
      keyword: state.searchParams?.keyword ?? "",
    }),
    [state.searchParams?.period, state.searchParams?.region, state.searchParams?.keyword]
  );

  const [searchParams, setSearchParams] = useState<NavbarSearchParams>({
    period: initialSearch.period,
    region: initialSearch.region,
    keyword: initialSearch.keyword,
  });

  // Tooltip state (10.2 재사용 전제)
  const [activeFestival, setActiveFestival] = useState<FestivalSummary | null>(null);
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);

  const closeTimerRef = useRef<number | null>(null);
  const hoveringTooltipRef = useRef(false);

  function clearCloseTimer() {
    if (closeTimerRef.current !== null) {
      window.clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }
  }

  function scheduleCloseTooltip() {
    clearCloseTimer();
    closeTimerRef.current = window.setTimeout(() => {
      if (hoveringTooltipRef.current) return;
      setActiveFestival(null);
      setAnchorRect(null);
    }, 120);
  }

  function openTooltip(row: SearchVolumeRow, anchorEl: HTMLElement) {
    clearCloseTimer();
    setActiveFestival({
      festivalId: row.festivalId,
      name: row.name,
      period: row.period,
      location: row.location,
    });
    setAnchorRect(anchorEl.getBoundingClientRect());
  }

  // 임시 리스트 데이터(백엔드 연동 전)
  const mockList: FestivalListItem[] = useMemo(
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

  const onOpenRead = (festivalId: FestivalListItem["festivalId"]) => {
    navigate("/busanfestival/read", { state: { festivalId } });
  };

  return (
    <div className="min-h-dvh" style={{ backgroundColor: "var(--c-bg)" }}>
      <Header
        defaultValues={searchParams}
        onSearch={(params) => {
          // 문서 전제: 검색 시 main-bottom 리스트 갱신
          setSearchParams(params);
        }}
      />

      <main className="mx-auto max-w-6xl px-4 py-4 xl:max-w-7xl 2xl:max-w-[90rem]">
        {/* Chart (10.1) */}
        <div className="mb-4">
          <SectionTitle>축제 검색량 순위</SectionTitle>
          <Panel>
            <SearchVolumeBarChart
              items={mockSearchVolumeTop5}
              onHoverLabel={(row, el) => openTooltip(row, el)}
              onLeaveLabel={() => scheduleCloseTooltip()}
            />
          </Panel>
        </div>

        {/* Tooltip (10.2) */}
        {activeFestival && anchorRect && (
          <FestivalTooltip
            festival={activeFestival}
            anchorRect={anchorRect}
            onClose={() => {
              clearCloseTimer();
              setActiveFestival(null);
              setAnchorRect(null);
            }}
            onMouseEnter={() => {
              hoveringTooltipRef.current = true;
              clearCloseTimer();
            }}
            onMouseLeave={() => {
              hoveringTooltipRef.current = false;
              scheduleCloseTooltip();
            }}
            onViewDetail={(festivalId) => {
              // 문서 전제: 상세보기 → /busanfestival/read + router state festivalId
              navigate("/busanfestival/read", { state: { festivalId } });
            }}
          />
        )}

        {/* Map: 항상 위 */}
        <div className="mb-4">
          <SectionTitle>지도 영역</SectionTitle>
          <Panel>
            <MapSection />
          </Panel>
        </div>

        {/* List: 모든 breakpoint에서 Map 아래 */}
        <div>
          <SectionTitle>축제 목록</SectionTitle>
          <Panel>
            {/* 검색조건 표시(기존 유지) */}
            <div
              className="mb-3 rounded-md px-3 py-2 text-xs"
              style={{
                backgroundColor: "rgba(184,205,234,0.22)",
                color: "var(--c-text)",
                border: "1px solid var(--c-border)",
              }}
            >
              검색조건: {searchParams.period || "시기(없음)"} / {searchParams.region || "지역(없음)"} /{" "}
              {searchParams.keyword || "검색어(없음)"}
            </div>

            {/* 정렬 UI(기존 유지: 추후 onClick 로직 연결) */}
            <div className="mb-3 flex items-center justify-between gap-2">
              <div
                className="rounded-md px-3 py-2 text-xs font-semibold"
                style={{
                  backgroundColor: "rgba(184,205,234,0.22)",
                  color: "var(--c-text)",
                  border: "1px solid var(--c-border)",
                }}
              >
                축제일순 | 인기순
              </div>
            </div>

            {/* 10.5 규칙 구현
                - gap: 폭 감소 시 먼저 줄어듦 (clamp)
                - columns: 3 → 2 → 1 (lg=3, sm=2, base=1)
            */}
            <div
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"
              style={{ gap: "clamp(12px, 2vw, 24px)" }}
            >
              {mockList.map((item) => (
                <FestivalCard key={String(item.festivalId)} item={item} onOpenRead={onOpenRead} />
              ))}
            </div>
          </Panel>
        </div>
      </main>
    </div>
  );
}
