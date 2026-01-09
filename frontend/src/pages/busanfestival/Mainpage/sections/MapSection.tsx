// src/pages/busanfestival/MainPage/sections/MapSection.tsx
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { loadKakaoMapsSDK } from "../../../../features/map/kakao";

// verbatimModuleSyntax 대응: type-only import
import type { FestivalSummary } from "../../../../components/overlays/FestivalTooltip/types";
import FestivalTooltip from "../../../../components/overlays/FestivalTooltip/FestivalTooltip";

type TooltipState = {
  festival: FestivalSummary;
  anchorRect: DOMRect;
  lat: number;
  lng: number;
} | null;

// 임시(목업) 데이터: 추후 백엔드 연동 시 교체
const mockFestivals: Array<FestivalSummary & { lat: number; lng: number }> = [
  { festivalId: 1, name: "부산 불꽃축제", period: "2026-10-01 ~ 2026-10-03", location: "광안리", lat: 35.1532, lng: 129.1186 },
  { festivalId: 2, name: "부산 바다축제", period: "2026-08-01 ~ 2026-08-07", location: "해운대", lat: 35.1587, lng: 129.1604 },
  { festivalId: 3, name: "국제영화제", period: "2026-10-05 ~ 2026-10-14", location: "영화의전당", lat: 35.1714, lng: 129.1270 },
];

export default function MapSection() {
  const navigate = useNavigate();

  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any | null>(null);
  const markersRef = useRef<any[]>([]);

  const [error, setError] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<TooltipState>(null);

  const appKey = (import.meta.env.VITE_KAKAO_MAP_APP_KEY as string | undefined) ?? "";

  const festivals = useMemo(() => mockFestivals, []);

  // 좌표 -> DOMRect(tooltip anchor) 변환
  const computeAnchorRect = (lat: number, lng: number) => {
    const container = containerRef.current;
    const map = mapRef.current;
    if (!container || !map || !window.kakao?.maps) return null;

    try {
      const latLng = new window.kakao.maps.LatLng(lat, lng);
      const projection = map.getProjection?.();
      if (!projection?.pointFromCoords) return null;

      const point = projection.pointFromCoords(latLng); // map container 기준 point
      const containerRect = container.getBoundingClientRect();

      // point가 container 내부 좌표라고 가정하고 viewport 기준으로 변환
      const x = containerRect.left + point.x;
      const y = containerRect.top + point.y;

      return new DOMRect(x, y, 0, 0);
    } catch {
      return null;
    }
  };

  useEffect(() => {
    if (!appKey) {
      setError("VITE_KAKAO_MAP_APP_KEY가 설정되지 않았습니다. .env.local에 JavaScript Key를 넣어주세요.");
      return;
    }

    let isMounted = true;

    (async () => {
      try {
        await loadKakaoMapsSDK({ appKey, libraries: ["services"] });

        if (!isMounted) return;
        const container = containerRef.current;
        if (!container) return;

        // map init (부산 중심)
        const center = new window.kakao.maps.LatLng(35.1796, 129.0756);
        const map = new window.kakao.maps.Map(container, { center, level: 7 });
        mapRef.current = map;

        // 지도 클릭 시 tooltip 닫기
        window.kakao.maps.event.addListener(map, "click", () => setTooltip(null));

        // 마커 생성
        markersRef.current.forEach((m) => m.setMap?.(null));
        markersRef.current = festivals.map((f) => {
          const pos = new window.kakao.maps.LatLng(f.lat, f.lng);
          const marker = new window.kakao.maps.Marker({ position: pos });
          marker.setMap(map);

          window.kakao.maps.event.addListener(marker, "click", () => {
            const anchorRect = computeAnchorRect(f.lat, f.lng);
            if (!anchorRect) return;

            setTooltip({
              festival: f,
              anchorRect,
              lat: f.lat,
              lng: f.lng,
            });
          });

          return marker;
        });

        // 지도 이동/줌 시 tooltip anchor 갱신(열려 있을 때만)
        const refreshTooltip = () => {
          setTooltip((prev) => {
            if (!prev) return prev;
            const nextRect = computeAnchorRect(prev.lat, prev.lng);
            if (!nextRect) return prev;
            return { ...prev, anchorRect: nextRect };
          });
        };

        window.kakao.maps.event.addListener(map, "center_changed", refreshTooltip);
        window.kakao.maps.event.addListener(map, "zoom_changed", refreshTooltip);
      } catch (e: any) {
        setError(e?.message ?? "Kakao Map 로딩 중 알 수 없는 오류가 발생했습니다.");
      }
    })();

    return () => {
      isMounted = false;
      markersRef.current.forEach((m) => m.setMap?.(null));
      markersRef.current = [];
      mapRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [appKey]);

  return (
    <section className="relative w-full">
      <div className="mb-2 flex items-end justify-between">
        <h2 className="text-base font-semibold text-[var(--text-strong)]">지도에서 축제를 확인하세요</h2>
        <p className="text-xs text-[var(--text-muted)]">마커 클릭 시 상세정보 툴팁</p>
      </div>

      <div className="relative overflow-hidden rounded-2xl border border-[var(--border-default)] bg-[var(--bg-surface)]">
        <div ref={containerRef} className="h-[320px] w-full sm:h-[380px] lg:h-[420px]" />

        {error && (
          <div className="absolute inset-0 grid place-items-center bg-[var(--bg-surface)]/90 p-4">
            <div className="max-w-[520px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] p-4 text-sm text-[var(--text-strong)]">
              <div className="font-semibold">지도 로딩 실패</div>
              <div className="mt-1 text-[var(--text-muted)]">{error}</div>
              <ul className="mt-3 list-disc pl-5 text-[var(--text-muted)]">
                <li>Developers 콘솔에서 Web 플랫폼 도메인(localhost:5173) 등록 여부 확인</li>
                <li>.env.local의 VITE_KAKAO_MAP_APP_KEY가 “JavaScript Key”인지 확인</li>
              </ul>
            </div>
          </div>
        )}

        {tooltip && (
          <FestivalTooltip
            festival={tooltip.festival}
            anchorRect={tooltip.anchorRect}
            onClose={() => setTooltip(null)}
            onOpenRead={() => navigate("/busanfestival/read", { state: { festivalId: tooltip.festival.festivalId } })}
          />
        )}
      </div>
    </section>
  );
}
