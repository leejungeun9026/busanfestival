import type { FestivalDetail } from "../ReadPage";

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

function buildKakaoDirectionsUrl(detail: FestivalDetail): string {
  // “도착지 저장”은 KakaoMap link/to 형태로 우선 구현(좌표가 있을 때)
  if (typeof detail.lat === "number" && typeof detail.lng === "number") {
    const name = encodeURIComponent(detail.name);
    return `https://map.kakao.com/link/to/${name},${detail.lat},${detail.lng}`;
  }

  // 좌표가 없으면 검색 기반으로 fallback
  const q = encodeURIComponent(detail.location || detail.name);
  return `https://map.kakao.com/?q=${q}`;
}

export default function DirectionsSection({ detail }: { detail: FestivalDetail }) {
  function openDirections() {
    const url = buildKakaoDirectionsUrl(detail);
    window.open(url, "_blank", "noopener,noreferrer");
  }

  return (
    <section>
      <SectionTitle>길찾기</SectionTitle>

      <Panel>
        {/* KakaoMap 연동 전: 컨테이너만 확보(문서 전제) */}
        <div
          className="relative h-[240px] rounded-xl sm:h-[280px] lg:h-[340px]"
          style={{
            backgroundColor: "var(--c-subtle)",
            border: "1px solid var(--c-border)",
          }}
        >
          {/* 실제 KakaoMap mount 지점(추후 구현) */}
          <div id="read-kakao-map" className="h-full w-full rounded-xl" />

          {/* 우측 하단 길찾기 버튼 */}
          <button
            type="button"
            onClick={openDirections}
            className="absolute bottom-3 right-3 rounded-lg px-4 py-2 text-sm font-semibold"
            style={{
              backgroundColor: "var(--c-accent)",
              color: "var(--c-surface)",
              border: "1px solid var(--c-border)",
            }}
          >
            길찾기
          </button>
        </div>
      </Panel>
    </section>
  );
}
