import { useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";

export type NavbarSearchParams = {
  period: string;  // 시기
  region: string;  // 지역
  keyword: string; // 검색어
};

type HeaderProps = {
  onSearch?: (params: NavbarSearchParams) => void;
  defaultValues?: Partial<NavbarSearchParams>;
};

export default function Header({ onSearch, defaultValues }: HeaderProps) {
  const navigate = useNavigate();
  const formRef = useRef<HTMLFormElement | null>(null);

  const fieldClass = useMemo(
    () => ["h-9 w-full rounded-md px-3 text-sm outline-none", "border"].join(" "),
    []
  );

  const buttonClass = useMemo(
    () => "h-9 rounded-md px-3 text-sm font-semibold whitespace-nowrap",
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
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:gap-4">
          {/* Brand: 텍스트 클릭 시 main 이동 (v0.3) */}
          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => navigate("/busanfestival/main")}
              className="truncate text-base font-semibold"
              style={{ color: "var(--neutral-0)" }}
            >
              BusanFestival
            </button>
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
            <select
              name="period"
              className={fieldClass}
              style={{
                backgroundColor: "var(--neutral-0)",
                color: "var(--c-text)",
                borderColor: "var(--c-border)",
              }}
              defaultValue={defaultValues?.period ?? ""}
            >
              <option value="" disabled>
                시기
              </option>
              <option value="all">전체</option>
              <option value="this_month">이번 달</option>
              <option value="next_month">다음 달</option>
            </select>

            <select
              name="region"
              className={fieldClass}
              style={{
                backgroundColor: "var(--neutral-0)",
                color: "var(--c-text)",
                borderColor: "var(--c-border)",
              }}
              defaultValue={defaultValues?.region ?? ""}
            >
              <option value="" disabled>
                지역
              </option>
              <option value="all">전체</option>
              <option value="busan">부산</option>
            </select>

            <input
              name="keyword"
              placeholder="검색어"
              className={`${fieldClass} xs:col-span-2 md:col-span-1`}
              style={{
                backgroundColor: "var(--neutral-0)",
                color: "var(--c-text)",
                borderColor: "var(--c-border)",
              }}
              defaultValue={defaultValues?.keyword ?? ""}
            />

            <button
              type="button"
              className={buttonClass}
              style={{
                backgroundColor: "rgba(184,205,234,0.18)",
                color: "var(--neutral-0)",
                border: "1px solid rgba(255,255,255,0.14)",
              }}
              onClick={() => {
                formRef.current?.reset();
                onSearch?.({ period: "", region: "", keyword: "" });
              }}
            >
              초기화
            </button>

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
