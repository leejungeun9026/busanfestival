import { useMemo } from "react";
import type { SearchVolumeItem, SearchVolumeRow } from "./model";
import { normalizeTop5 } from "./model";

type Props = {
  items: SearchVolumeItem[];
  onHoverLabel?: (row: SearchVolumeRow, anchorEl: HTMLElement) => void;
  onLeaveLabel?: () => void;
};

function formatText(v?: string) {
  const t = (v ?? "").trim();
  return t.length ? t : "(정보 없음)";
}

const TICKS = [60, 70, 80, 90, 100] as const;

export default function SearchVolumeBarChart({ items, onHoverLabel, onLeaveLabel }: Props) {
  const rows = useMemo(() => normalizeTop5(items), [items]);

  return (
    <div
      className="rounded-lg p-8"
      style={{ backgroundColor: "var(--c-subtle)", border: "1px solid var(--c-border)" }}
    >
      {/* Title */}
      <div className="mb-4">
        <div className="text-center text-xl font-bold" style={{ color: "var(--c-text)" }}>
          최근 Hype 받는 축제예요
        </div>
        <div className="mt-1 text-center text-xs" style={{ color: "var(--c-muted)" }}>
          1위=100 기준 상대비율
        </div>
      </div>

      {/* Plot Area (axes + bars) */}
      <div
        className="relative w-9/10 overflow-visible rounded-md"
        style={{
          // x축/ y축 역할
          borderLeft: "5px solid var(--c-border)", // y-axis
          borderBottom: "5px solid var(--c-border)", // x-axis
        }}
      >
        {/* plot padding: 축 선과 내용 간 최소 간격 */}
        <div className="relative overflow-visible pb-2 pt-7">
          <div className="space-y-5">
            {rows.map((row, idx) => {
              const label = formatText(row.name);
              const score = row.normalizedScore;

              return (
                <div key={String(row.festivalId)} className="relative">
                  {/* bar track */}
                  <div
                    className="h-15 w-full rounded-md"
                    style={{
                      // backgroundColor: "var(--c-surface)",
                      // border: "1px solid var(--c-border)",
                    }}
                  >
                    {/* bar fill */}
                    <div
                      className="h-full rounded-md"
                      style={{
                        width: `${score}%`,
                        backgroundColor: idx === 0 ? "var(--c-accent)" : "rgba(184,205,234,0.95)",
                        transition: "width 200ms ease",
                      }}
                      aria-label={`${label} 점수 ${Math.round(score)}`}
                    />
                  </div>

                  {/* label: bar 끝나는 지점 바로 오른쪽 */}
                  <button
                    type="button"
                    className="absolute top-1/2 -translate-y-1/2 truncate text-left text-sm font-semibold underline-offset-4 hover:underline"
                    style={{
                      // bar 끝(%) + 8px 지점에 배치 (오버플로우 허용)
                      left: `calc(${score}% + 8px)`,
                      maxWidth: "18rem",
                      color: "var(--c-text)",
                    }}
                    onMouseEnter={(e) => onHoverLabel?.(row, e.currentTarget)}
                    onMouseLeave={() => onLeaveLabel?.()}
                    title={label}
                  >
                    {label}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      {/* X-axis ticks: plot 내부(=바의 가로 길이)와 정확히 정렬 */}
      <div className="mt-3">
        <div className="grid grid-cols-5 text-[11px]" style={{ color: "var(--c-muted)" }}>
          {TICKS.map((t) => (
            <div key={t} className="text-center">
              {t}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
