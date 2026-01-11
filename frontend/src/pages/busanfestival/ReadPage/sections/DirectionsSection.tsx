import { useEffect, useMemo, useRef, useState } from "react";
import type { FestivalDetail } from "../ReadPage";
import { loadKakaoMapsSDK } from "../../../../features/map/kakao";

function SectionTitle({ children }: { children: string }) {
  return (
    <h2 className="mb-2 text-sm font-semibold" style={{ color: "var(--c-text)" }}>
      {children}
    </h2>
  );
}

function Panel({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-xl p-4"
      style={{
        backgroundColor: "var(--c-surface)",
        border: "1px solid var(--c-border)",
      }}
    >
      {children}
    </div>
  );
}

/** Directions용 최소 타입(명시적 any 회피) */
type KakaoMarker = { setMap?: (map: unknown | null) => void };

type KakaoNamespace = {
  maps: {
    LatLng: new (lat: number, lng: number) => unknown;
    Map: new (container: HTMLElement, options: { center: unknown; level: number }) => unknown;
    Marker: new (options: { position: unknown }) => KakaoMarker;
  };
};

function buildKakaoDirectionsUrl(detail: FestivalDetail): string {
  // “도착지 저장”을 가장 안정적으로 만족: link/to
  if (typeof detail.lat === "number" && typeof detail.lng === "number") {
    const name = encodeURIComponent(detail.name);
    return `https://map.kakao.com/link/to/${name},${detail.lat},${detail.lng}`;
  }

  // 좌표가 없으면 검색 기반 fallback
  const q = encodeURIComponent(detail.location || detail.name);
  return `https://map.kakao.com/?q=${q}`;
}

export default function DirectionsSection({ detail }: { detail: FestivalDetail }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const markerRef = useRef<KakaoMarker | null>(null);

  const [error, setError] = useState<string | null>(null);

  const appKey = (import.meta.env.VITE_KAKAO_MAP_APP_KEY as string | undefined) ?? "";

  const hasCoords = typeof detail.lat === "number" && typeof detail.lng === "number";

  const kakaoDirectionsUrl = useMemo(() => buildKakaoDirectionsUrl(detail), [detail]);

  useEffect(() => {
    // 좌표가 없으면 “지도 표시 불가” 상태로만 유지
    if (!hasCoords) {
      setError("축제 좌표(lat/lng)가 없어 지도를 표시할 수 없습니다. (현재 mock 단계)");
      return;
    }

    if (!appKey) {
      // MainPage MapSection과 동일한 키 요구 :contentReference[oaicite:5]{index=5}
      setError("VITE_KAKAO_MAP_APP_KEY가 설정되지 않았습니다. .env.local에 JavaScript Key를 넣어주세요.");
      return;
    }

    let isMounted = true;

    (async () => {
      try {
        setError(null);

        // MainPage와 동일 로더 재사용: 스크립트 중복 로드 방지 :contentReference[oaicite:6]{index=6}
        await loadKakaoMapsSDK({ appKey });

        if (!isMounted) return;

        const container = containerRef.current;
        if (!container) return;

        const kakao = (window.kakao as unknown as KakaoNamespace) || undefined;
        if (!kakao?.maps) {
          setError("Kakao Maps SDK가 로드되었지만 window.kakao.maps가 준비되지 않았습니다.");
          return;
        }

        const center = new kakao.maps.LatLng(detail.lat!, detail.lng!);
        // level: ReadPage는 “상세 위치 중심”이므로 더 가깝게
        const map = new kakao.maps.Map(container, { center, level: 3 });

        // 단일 마커
        markerRef.current?.setMap?.(null);
        const marker = new kakao.maps.Marker({ position: center });
        marker.setMap?.(map);
        markerRef.current = marker;
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : "Kakao Map 로딩 중 알 수 없는 오류가 발생했습니다.";
        setError(msg);
      }
    })();

    return () => {
      isMounted = false;
      markerRef.current?.setMap?.(null);
      markerRef.current = null;
    };
  }, [appKey, detail.lat, detail.lng, hasCoords]);

  function openDirections() {
    window.open(kakaoDirectionsUrl, "_blank", "noopener,noreferrer");
  }

  return (
    <section>
      <SectionTitle>길찾기</SectionTitle>

      <Panel>
        <div
          className="relative overflow-hidden rounded-xl"
          style={{
            backgroundColor: "var(--c-subtle)",
            border: "1px solid var(--c-border)",
          }}
        >
          {/* 지도 영역 */}
          <div
            ref={containerRef}
            className="h-[240px] w-full sm:h-[280px] lg:h-[340px]"
            aria-label="축제 위치 지도"
          />

          {/* 지도 내부 우측 하단: 길찾기 버튼 */}
          <button
            type="button"
            onClick={openDirections}
            disabled={!hasCoords}
            className="absolute z-10 bottom-3 right-3 rounded-lg px-4 py-2 text-sm font-semibold"
            style={{
              backgroundColor: "var(--c-accent)",
              color: "var(--c-surface)",
              border: "1px solid var(--c-border)",
              opacity: hasCoords ? 1 : 0.35,
              cursor: hasCoords ? "pointer" : "default",
            }}
            title={!hasCoords ? "좌표가 없어 길찾기를 사용할 수 없습니다." : "카카오맵에서 길찾기"}
            aria-disabled={!hasCoords}
          >
            길찾기
          </button>

          {/* 에러 오버레이 */}
          {error && (
            <div
              className="absolute inset-0 grid place-items-center p-4 text-center text-sm"
              style={{
                backgroundColor: "rgba(255,255,255,0.72)",
                color: "var(--c-muted)",
              }}
            >
              <div className="max-w-[520px]">
                <div className="font-semibold" style={{ color: "var(--c-text)" }}>
                  지도 로딩 실패
                </div>
                <div className="mt-1">{error}</div>
                {!appKey && (
                  <ul className="mt-3 list-disc pl-5 text-left">
                    <li>Kakao Developers Web 플랫폼에 도메인(localhost:5173) 등록 여부 확인</li>
                    <li>.env.local의 VITE_KAKAO_MAP_APP_KEY가 “JavaScript Key”인지 확인</li>
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      </Panel>
    </section>
  );
}
