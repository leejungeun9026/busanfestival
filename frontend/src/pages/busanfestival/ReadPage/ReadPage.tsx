import { useNavigate } from "react-router-dom";
import Header, { type NavbarSearchParams } from "../../../components/layout/Header/Header";

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-2 text-sm font-semibold" style={{ color: "var(--c-text)" }}>
      {children}
    </h2>
  );
}

function Panel({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-xl p-3"
      style={{
        backgroundColor: "var(--c-surface)",
        border: "1px solid var(--c-border)",
      }}
    >
      {children}
    </div>
  );
}

export default function ReadPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-dvh" style={{ backgroundColor: "var(--c-bg)" }}>
      <Header
        onSearch={(params: NavbarSearchParams) => {
          // 문서 전제: Read에서 검색하면 main으로 이동 + 조건 전달
          navigate("/busanfestival/main", { state: { searchParams: params } });
        }}
      />

      <main className="mx-auto max-w-6xl px-4 py-4 space-y-4 xl:max-w-7xl 2xl:max-w-[90rem]">
        {/* Festival Info */}
        <section>
          <SectionTitle>축제 정보</SectionTitle>
          <Panel>
            <div className="space-y-2" style={{ color: "var(--c-text)" }}>
              <div className="text-lg font-semibold">(축제명)</div>
              <div className="text-sm" style={{ color: "var(--c-muted)" }}>
                (진행 중 여부)
              </div>
              <div className="text-sm" style={{ color: "var(--c-muted)" }}>
                (최저기온, 최고기온)
              </div>
              <div className="text-sm" style={{ color: "var(--c-muted)" }}>
                (축제 기간)
              </div>
              <div className="text-sm" style={{ color: "var(--c-muted)" }}>
                (운영 시간)
              </div>
              <div className="text-sm" style={{ color: "var(--c-muted)" }}>
                (문의처 전화번호)
              </div>
            </div>
          </Panel>
        </section>

        {/* Images */}
        <section>
          <SectionTitle>이미지 영역</SectionTitle>
          <Panel>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div
                  key={i}
                  className="aspect-video rounded-lg"
                  style={{
                    backgroundColor: "var(--c-subtle)",
                    border: "1px solid var(--c-border)",
                  }}
                />
              ))}
            </div>
          </Panel>
        </section>

        {/* Directions */}
        <section>
          <SectionTitle>길찾기</SectionTitle>
          <Panel>
            <div
              className="h-[220px] rounded-lg sm:h-[260px] lg:h-[320px]"
              style={{
                backgroundColor: "var(--c-subtle)",
                border: "1px solid var(--c-border)",
              }}
            >
              {/* 문서 전제: 길찾기 지도는 현재 영역만 */}
            </div>
          </Panel>
        </section>
      </main>
    </div>
  );
}
