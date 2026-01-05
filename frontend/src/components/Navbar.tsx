import { useNavigate } from "react-router-dom";

type NavbarProps = {
  onSearch?: (keyword: string) => void;
}

export default function Navbar({ onSearch } : NavbarProps) {
  const navigate = useNavigate();

  return(
    <header
      className="w-full"
      style={{backgroundColor: "var(--c-primary)", color: "var(--c-bg)"}}
    >
      <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3">
        {/* Home */}
        <button
          type="button"
          onClick={()=>navigate("/busanfestival/main")}
          className="rounded-md px-3 py-2 text-sm font-semibold"
          style={{backgroundColor: "rgba(217,217,217,0.12)"}}
        >
          Home
        </button>

        {/* Title => brand name */}
        <div className="min-w-0 flex-1">
          <div className="truncate text-base font-semibold">BusanFestival</div>
        </div>

        {/* Search (Read로 바로 이동하는 용도) */}
        <form
          className="flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            const form = e.currentTarget;
            const input = form.elements.namedItem("q") as HTMLInputElement | null;
            const keyword = (input?.value ?? "").trim();
            if (!keyword) return;
            onSearch?.(keyword)
          }}
        >
          <input
            name="q"
            placeholder="Search"
            className="h-9 w-44 rounded-md px-3 text-sm outline-none md:w-64"
            style={{
              backgroundColor: "var(--c-bg)",
              color: "var(--c-text)",
              border: "1px solid var(--c-surfave)",
            }}
          />
          <button
            type="submit"
            className="h-9 rounded-md px-3 text-sm font-semibold"
            style={{backgroundColor: "var(--c-accent)", color:"var(--c-primary)"}}
            onClick={() => {
              // "검색으로 read 집입"을 목적으로 함
              navigate("/busanfestival/read");
            }}
          >
            Go
          </button>
        </form>
      </div>
    </header>
  )
}

