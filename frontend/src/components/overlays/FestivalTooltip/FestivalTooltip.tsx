import type { FestivalSummary } from "./types";

type Props = {
  festival: FestivalSummary;
  anchorRect: DOMRect;
  onClose: () => void;
  onViewDetail: (festivalId: FestivalSummary["festivalId"]) => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
};

function formatText(v?: string) {
  const t = (v ?? "").trim();
  return t.length ? t : "(정보 없음)";
}

function computePosition(anchorRect: DOMRect) {
  const gap = 10;
  const width = 280;
  const heightGuess = 160;

  const desiredLeft = anchorRect.right + gap;
  const desiredTop = anchorRect.top - 6;

  const vw = window.innerWidth;
  const vh = window.innerHeight;

  const left = Math.min(Math.max(12, desiredLeft), Math.max(12, vw - width - 12));
  const top = Math.min(Math.max(12, desiredTop), Math.max(12, vh - heightGuess - 12));

  return { top, left, width };
}

export default function FestivalTooltip({
  festival,
  anchorRect,
  onClose,
  onViewDetail,
  onMouseEnter,
  onMouseLeave,
}: Props) {
  const pos = computePosition(anchorRect);

  return (
    <div
      role="tooltip"
      className="fixed rounded-xl p-3"
      style={{
        top: pos.top,
        left: pos.left,
        width: pos.width,
        zIndex: 50,
        backgroundColor: "var(--c-surface)",
        border: "1px solid var(--c-border)",
        color: "var(--c-text)",
        boxShadow: "var(--overlay-shadow, 0 10px 30px rgba(0, 8, 19, 0.18))",
      }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold">{formatText(festival.name)}</div>
          <div className="mt-1 text-xs" style={{ color: "var(--c-muted)" }}>
            {formatText(festival.period)}
          </div>
          <div className="mt-1 text-xs" style={{ color: "var(--c-muted)" }}>
            {formatText(festival.location)}
          </div>
        </div>

        <button
          type="button"
          className="h-7 w-7 shrink-0 rounded-md text-sm font-semibold"
          style={{
            border: "1px solid var(--c-border)",
            backgroundColor: "var(--c-subtle)",
            color: "var(--c-text)",
          }}
          onClick={onClose}
          aria-label="툴팁 닫기"
          title="닫기"
        >
          X
        </button>
      </div>

      <div className="mt-3 flex justify-end">
        <button
          type="button"
          className="h-9 rounded-md px-3 text-sm font-semibold"
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
          onClick={() => onViewDetail(festival.festivalId)}
        >
          상세보기
        </button>
      </div>
    </div>
  );
}
