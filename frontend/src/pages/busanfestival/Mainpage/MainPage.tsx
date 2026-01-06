import { useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Header, { type NavbarSearchParams } from "../../../components/layout/Header/Header";
import { SearchVolumeBarChart, mockSearchVolumeTop5 } from "../../../components/charts/SearchVolumeBarChart";
import { FestivalTooltip, type FestivalSummary } from "../../../components/overlays/FestivalTooltip";
import type { SearchVolumeRow } from "../../../components/charts/SearchVolumeBarChart";

type LocationState = {
  searchParams?: Partial<NavbarSearchParams>;
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

        {/* Map + List (기존 유지) */}
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
          {/* Map */}
          <section className="lg:col-span-7">
            <SectionTitle>지도 영역</SectionTitle>
            <Panel>
              <div
                className="h-[320px] rounded-lg sm:h-[360px] lg:h-[420px]"
                style={{ backgroundColor: "var(--c-subtle)", border: "1px solid var(--c-border)" }}
              >
                {/* 10.3 구현 예정 */}
              </div>
            </Panel>
          </section>

          {/* List */}
          <section className="lg:col-span-5">
            <SectionTitle>축제 목록</SectionTitle>
            <Panel>
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

              <div className="space-y-2">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div
                    key={i}
                    className="rounded-lg p-3"
                    style={{
                      backgroundColor: "var(--c-surface)",
                      border: "1px solid var(--c-border)",
                    }}
                  >
                    <div className="text-sm font-semibold" style={{ color: "var(--c-text)" }}>
                      (축제명)
                    </div>
                    <div className="mt-1 text-xs" style={{ color: "var(--c-muted)" }}>
                      (운영기간) · (위치정보)
                    </div>
                  </div>
                ))}
              </div>
            </Panel>
          </section>
        </div>
      </main>
    </div>
  );
}
