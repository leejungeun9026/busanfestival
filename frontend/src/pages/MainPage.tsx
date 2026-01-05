import Navbar from "../components/Navbar";

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
      style={{ backgroundColor: "var(--c-surface)", border: "1px solid var(--c-primary)" }}
    >
      {children}
    </div>
  );
}

export default function MainPage() {
  return (
    <div className="min-h-dvh" style={{backgroundColor: "var(--c-bg)"}}>
      <Navbar/>

      <main className="mx-auto max-w-6xl px-4 px-4">
        {/* Chart */}
        <div className="mb-4">
          <SectionTitle>Bar Chart (가로형)</SectionTitle>
          <Panel>
            <div className="h-28 rounded-lg" style={{backgroundColor: "var(--c-bg)"}}>
              {/* 차트가 들어올 예정 */}
            </div>
          </Panel>
        </div>

        {/* Map + List */}
        <div className="grid grid-cols-12 gap-4">
          {/* Map */}
          <section className="col-span-12 md:col-span-7">
            <SectionTitle>지도 영역</SectionTitle>
            <Panel>
              <div className="h-[360px] rounded-lg" style={{backgroundColor: "var(--c-bg)"}}>
                {/* 지도가 들어올 예정 */}
              </div>
            </Panel>
          </section>

          {/* List */}
          <section className="col-span-12 md:col-span-5">
            <SectionTitle>축제 목록</SectionTitle>
            <Panel>
              <div className="mb-3 flex items-center justify-between gap-2">
                <div
                  className="rounded-md px-3 py-2 text-xs font-semibold"
                  style={{backgroundColor: "var(--c-bg)", color: "var(--c-text)"}}
                >
                  축제일순 | 인기순
                </div>
              </div>

              <div className="space-y-2">
                {/* 리스트 구현은 추후에. 박스만 생성 */}
                {Array.from({length:6}).map((_, i) => (
                  <div
                    key={i}
                    className="rounded-lg p-3"
                    style={{backgroundColor: "var(--c-bg)", border: "1px solid var(--c-surface)"}}
                  >
                    <div className="text-sm font-semibold" style={{color: "var(--c-text)"}}>
                      (축제명)
                    </div>
                    <div className="mt-1 text-xs" style={{color:"var(--c-text)"}}>
                      (운영기간) · (위치정보)
                    </div>
                  </div>
                ))}
              </div>
            </Panel>
          </section>
        </div>
      </main>
    </div>
  )
}
