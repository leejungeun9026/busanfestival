import { useEffect, useMemo, useRef, useState } from "react";

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

function ArrowIcon({ dir }: { dir: "left" | "right" }) {
  const rotate = dir === "left" ? "rotate(180deg)" : "none";
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" style={{ transform: rotate }} aria-hidden="true">
      <path
        d="M9 18l6-6-6-6"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function NavButton({
  dir,
  disabled,
  onClick,
}: {
  dir: "left" | "right";
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={dir === "left" ? "이전 이미지" : "다음 이미지"}
      className="grid h-10 w-10 place-items-center rounded-full"
      style={{
        backgroundColor: "var(--c-surface)",
        border: "1px solid var(--c-border)",
        color: "var(--c-text)",
        opacity: disabled ? 0.25 : 1,
        cursor: disabled ? "default" : "pointer",
        boxShadow: "var(--overlay-shadow)",
      }}
    >
      <ArrowIcon dir={dir} />
    </button>
  );
}

export default function ImagesSection({
  festivalName,
  images,
}: {
  festivalName: string;
  images: string[];
}) {
  // 요구: 한 번에 3개가 "보이되", 이동은 1개씩(미끄러짐)
  const visibleCount = 3;

  // 실제 이미지가 3개 미만이어도 레이아웃 슬롯은 3개를 유지
  const renderList = useMemo(() => {
    if (images.length >= visibleCount) return images;
    return [...images, ...Array.from({ length: visibleCount - images.length }).map(() => "")];
  }, [images]);

  const maxIndex = Math.max(0, images.length - visibleCount); // 이동 가능한 뷰의 마지막 인덱스
  const [index, setIndex] = useState(0);

  const canPrev = index > 0;
  const canNext = index < maxIndex;

  const viewportRef = useRef<HTMLDivElement | null>(null);
  const [slotWidth, setSlotWidth] = useState(0);

  function scrollToIndex(nextIndex: number, behavior: ScrollBehavior) {
    const viewport = viewportRef.current;
    if (!viewport) return;
    if (slotWidth <= 0) return;
    viewport.scrollTo({ left: nextIndex * slotWidth, behavior });
  }

  function goPrev() {
    if (!canPrev) return;
    setIndex((prev) => {
      const next = Math.max(0, prev - 1);
      scrollToIndex(next, "smooth");
      return next;
    });
  }

  function goNext() {
    if (!canNext) return;
    setIndex((prev) => {
      const next = Math.min(maxIndex, prev + 1);
      scrollToIndex(next, "smooth");
      return next;
    });
  }

  // viewport width 기준으로 "한 슬롯(= 한 장 이동 단위)" 픽셀 폭 계산
  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) return;

    const ro = new ResizeObserver(() => {
      const w = viewport.clientWidth;
      const sw = Math.floor(w / visibleCount);
      setSlotWidth(sw);
      // 리사이즈 시 현재 index 위치로 즉시 보정
      window.requestAnimationFrame(() => scrollToIndex(index, "auto"));
    });

    ro.observe(viewport);

    // 최초 계산
    const w0 = viewport.clientWidth;
    const sw0 = Math.floor(w0 / visibleCount);
    setSlotWidth(sw0);
    window.requestAnimationFrame(() => scrollToIndex(index, "auto"));

    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Indicator: "뷰 단위" 개수 = maxIndex + 1 (이동도 1개씩이므로)
  const viewCount = Math.max(1, maxIndex + 1);
  // thumb 폭(부모 바 기준 %) — 기존과 동일(한 칸 단위)
  const thumbWidthPct = 100 / viewCount;
  // left는 "부모 바 기준 %"로 계산해야 끝까지 도달함
  // - viewCount=1이면 분모 0 방지
  const denom = Math.max(1, viewCount - 1);
  // left는 0% ~ (100 - thumbWidthPct)% 범위에서 이동
  const thumbLeftPct = (index / denom) * (100 - thumbWidthPct);

  return (
    <section>
      <SectionTitle>이미지 영역</SectionTitle>

      <Panel>
        {/* 버튼은 카드 영역 바깥(좌/우) */}
        <div className="flex items-center justify-center gap-4">
          <NavButton dir="left" disabled={!canPrev} onClick={goPrev} />

          {/* Carousel viewport */}
          <div
            ref={viewportRef}
            className="w-full overflow-x-auto overflow-y-hidden [scrollbar-width:none]"
            style={{
              scrollBehavior: "smooth",
            }}
          >
            {/* 스크롤바 숨김(가능한 브라우저 범위에서) */}
            <div>
              <div className="flex">
                {renderList.map((src, i) => {
                  const isPlaceholder = !src;
                  return (
                    <div
                      key={`${i}-${src ? "img" : "ph"}`}
                      className="shrink-0"
                      style={{ width: slotWidth > 0 ? `${slotWidth}px` : undefined }}
                    >
                      {/* 각 슬롯 내 카드 크기 80% */}
                      <div className="mx-auto w-4/5">
                        <div
                          className="aspect-[3/4] overflow-hidden rounded-xl"
                          style={{
                            backgroundColor: "var(--c-subtle)",
                            border: "1px solid var(--c-border)",
                          }}
                        >
                          {!isPlaceholder ? (
                            <img
                              src={src}
                              alt={`${festivalName} 이미지 ${i + 1}`}
                              className="h-full w-full object-cover"
                              loading="lazy"
                              draggable={false}
                            />
                          ) : (
                            <div className="grid h-full w-full place-items-center text-xs" style={{ color: "var(--c-muted)" }}>
                              (이미지 없음)
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <NavButton dir="right" disabled={!canNext} onClick={goNext} />
        </div>

        {/* Indicator: 카드 이동과 동일하게 “슬라이딩” */}
        <div className="mt-4 flex items-center justify-center">
          <div
            className="relative h-2 w-56 overflow-hidden rounded-full"
            style={{
              backgroundColor: "color-mix(in oklab, var(--c-border) 70%, transparent)",
              border: "1px solid var(--c-border)",
            }}
            aria-label="이미지 진행 표시"
          >
            {/* thumb */}
            <div
              className="absolute top-0 h-full rounded-full"
              style={{
                left: `${thumbLeftPct}%`,
                width: `${thumbWidthPct}%`,
                backgroundColor: "var(--c-accent)",
                transition: "left 320ms ease-out",
              }}
            />
          </div>
        </div>

        {/* Divider */}
        <hr className="mt-4" style={{ borderColor: "var(--c-border)" }} />
      </Panel>
    </section>
  );
}
