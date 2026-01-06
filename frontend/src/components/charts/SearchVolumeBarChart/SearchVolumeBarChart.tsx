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

export default function SearchVolumeBarChart({ items, onHoverLabel, onLeaveLabel }: Props) {
  const rows = useMemo(() => normalizeTop5(items), [items]);

  return (
    <div
      className="rounded-lg p-3"
      style={{ backgroundColor: "var(--c-subtle)", border: "1px solid var(--c-border)" }}
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="text-sm font-semibold" style={{ color: "var(--c-text)" }}>
          최근 Hype 받는 축제예요
        </div>
        <div className="text-xs" style={{ color: "var(--c-muted)" }}>
          1위=100 기준 상대비율
        </div>
      </div>

      <div className="space-y-2">
        {rows.map((row, idx) => {
          const label = formatText(row.name);
          const score = row.normalizedScore;

          return (
            <div key={String(row.festivalId)} className="grid grid-cols-12 items-center gap-3">
              {/* Bar */}
              <div className="col-span-8">
                <div
                  className="h-6 w-full overflow-hidden rounded-md"
                  style={{
                    backgroundColor: "var(--c-surface)",
                    border: "1px solid var(--c-border)",
                  }}
                >
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
              </div>

              {/* Label (Tooltip trigger) */}
              <div className="col-span-4">
                <button
                  type="button"
                  className="w-full truncate text-left text-sm font-semibold underline-offset-4 hover:underline"
                  style={{ color: "var(--c-text)" }}
                  onMouseEnter={(e) => onHoverLabel?.(row, e.currentTarget)}
                  onMouseLeave={() => onLeaveLabel?.()}
                  title={label}
                >
                  {label}
                </button>
                <div className="mt-0.5 text-xs" style={{ color: "var(--c-muted)" }}>
                  {Math.round(score)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 스토리보드 느낌의 눈금(고정 표시) */}
      <div className="mt-4 flex items-center justify-between text-[11px]" style={{ color: "var(--c-muted)" }}>
        <span>60</span>
        <span>70</span>
        <span>80</span>
        <span>90</span>
        <span>100</span>
      </div>
    </div>
  );
}
