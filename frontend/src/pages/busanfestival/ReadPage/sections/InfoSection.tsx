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

function Chip({ children }: { children: string }) {
  return (
    <span
      className="inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold"
      style={{
        backgroundColor: "var(--c-soft)",
        color: "var(--c-text)",
        border: "1px solid var(--c-border)",
      }}
    >
      {children}
    </span>
  );
}

export default function InfoSection({ detail }: { detail: FestivalDetail }) {
  const tempText =
    detail.tempMin !== null && detail.tempMax !== null
      ? `최저 ${detail.tempMin}° / 최고 ${detail.tempMax}°`
      : "최저/최고기온 (준비 중)";

  return (
    <section>
      <SectionTitle>축제 정보</SectionTitle>

      <Panel>
        <div className="space-y-3">
          {/* 1행: 축제명 (heading, bold) */}
          <div
            className="text-2xl font-bold sm:text-3xl"
            style={{ color: "var(--c-text)" }}
          >
            {detail.name}
          </div>

          {/* 2행: 진행중 여부 + 기온 (chip) */}
          <div className="flex flex-wrap items-center gap-2">
            <Chip>{detail.isOngoing ? "진행 중" : "진행 종료"}</Chip>
            <Chip>{tempText}</Chip>
          </div>

          {/* 3~5행 */}
          <div className="space-y-2">
            <div className="text-sm" style={{ color: "var(--c-muted)" }}>
              축제 기간
            </div>
            <div className="text-base" style={{ color: "var(--c-text)" }}>
              {detail.period}
            </div>

            <div className="text-sm" style={{ color: "var(--c-muted)" }}>
              운영 시간
            </div>
            <div className="text-base" style={{ color: "var(--c-text)" }}>
              {detail.hours}
            </div>

            <div className="text-sm" style={{ color: "var(--c-muted)" }}>
              문의처 전화번호
            </div>
            <div className="text-base" style={{ color: "var(--c-text)" }}>
              {detail.phone}
            </div>
          </div>
        </div>
      </Panel>
    </section>
  );
}
