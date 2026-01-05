import { useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";

export type NavbarSearchParams = {
  period: string; // 시기
  region: string; // 지역
  keyword: string; // 검색어
};

type NavbarProps = {
  onSearch?: (params: NavbarSearchParams) => void;
};

export default function Navbar({ onSearch }: NavbarProps) {
  const navigate = useNavigate();
  const formRef = useRef<HTMLFormElement | null>(null);

  const fieldClass = useMemo(
    () =>
      [
        "h-9 w-full rounded-md px-3 text-sm outline-none",
        "border",
      ].join(" "),
    []
  );

  const buttonClass = useMemo(
    () =>
      "h-9 rounded-md px-3 text-sm font-semibold whitespace-nowrap",
    []
  );

  return (
    <header
      className="w-full border-b"
      style={{
        backgroundColor: "var(--c-primary)",
        color: "var(--neutral-0)",
        borderColor: "rgba(255,255,255,0.10)",
      }}
    >
      <div className="mx-auto max-w-6xl px-4 py-3 xl:max-w-7xl 2xl:max-w-[90rem]">
        {/* 모바일: 2줄(브랜드/액션) + (검색폼) / 데스크탑: 1줄 */}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-4">
          {/* Brand */}
          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => navigate("/busanfestival/main")}
              className="truncate text-base font-semibold"
              style={{ color: "var(--neutral-0)" }}
            >
              BusanFestival
            </button>

            {/* (필요 시) 우측에 최소 액션 배치 가능 */}
          </div>

          {/* Search Form (v0.3: 시기/지역/검색어 + 초기화 + 검색) */}
          <form
            ref={formRef}
            className="grid w-full grid-cols-1 gap-2 xs:grid-cols-2 md:ml-auto md:max-w-[760px] md:grid-cols-5"
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);

              const params: NavbarSearchParams = {
                period: String(fd.get("period") ?? "").trim(),
                region: String(fd.get("region") ?? "").trim(),
                keyword: String(fd.get("keyword") ?? "").trim(),
              };

              onSearch?.(params);
            }}
          >
            {/* 시기 */}
            <select
              name="period"
              className={fieldClass}
              style={{
                backgroundColor: "var(--neutral-0)",
                color: "var(--c-text)",
                borderColor: "var(--c-border)",
              }}
              defaultValue=""
            >
              <option value="" disabled>
                시기
              </option>
              <option value="all">전체</option>
              <option value="this_month">이번 달</option>
              <option value="next_month">다음 달</option>
            </select>

            {/* 지역 */}
            <select
              name="region"
              className={fieldClass}
              style={{
                backgroundColor: "var(--neutral-0)",
                color: "var(--c-text)",
                borderColor: "var(--c-border)",
              }}
              defaultValue=""
            >
              <option value="" disabled>
                지역
              </option>
              <option value="all">전체</option>
              <option value="busan">부산</option>
            </select>

            {/* 검색어 */}
            <input
              name="keyword"
              placeholder="검색어"
              className={`${fieldClass} xs:col-span-2 md:col-span-1`}
              style={{
                backgroundColor: "var(--neutral-0)",
                color: "var(--c-text)",
                borderColor: "var(--c-border)",
              }}
            />

            {/* 초기화 */}
            <button
              type="button"
              className={buttonClass}
              style={{
                backgroundColor: "rgba(184,205,234,0.18)", // soft (알파)
                color: "var(--neutral-0)",
                border: "1px solid rgba(255,255,255,0.14)",
              }}
              onClick={() => {
                formRef.current?.reset();
                // 초기화 시에도 main-bottom 리스트 갱신이 필요하면 빈 조건으로 호출
                onSearch?.({ period: "", region: "", keyword: "" });
              }}
            >
              초기화
            </button>

            {/* 검색 */}
            <button
              type="submit"
              className={buttonClass}
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
              검색
            </button>
          </form>
        </div>
      </div>
    </header>
  );
}
