import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import Header from "../../../components/layout/Header/Header";
import type { NavbarSearchParams } from "../../../components/layout/Header/Header";

import InfoSection from "./sections/InfoSection";
import ImagesSection from "./sections/ImagesSection";
import DirectionsSection from "./sections/DirectionsSection";

type FestivalId = string | number;

export type FestivalDetail = {
  festivalId: FestivalId;
  name: string;
  isOngoing: boolean;
  tempMin: number | null;
  tempMax: number | null;
  period: string;
  hours: string;
  phone: string;
  location: string;
  lat?: number;
  lng?: number;
  images: string[];
};

type LocationState = {
  festivalId?: FestivalId;
};

const MOCK_FESTIVAL_DETAILS: Record<string, FestivalDetail> = {
  "1": {
    festivalId: 1,
    name: "부산 불꽃 축제",
    isOngoing: true,
    tempMin: 8,
    tempMax: 14,
    period: "2026.01.10 ~ 2026.01.20",
    hours: "18:00 ~ 22:00",
    phone: "051-000-0000",
    location: "부산광역시 해운대구 일대",
    lat: 35.1587,
    lng: 129.1604,
    images: [
      "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1520975958225-62e8794f18e2?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1520975965870-35d9f4b5b5bd?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?auto=format&fit=crop&w=1200&q=60",
    ],
  },
  "2": {
    festivalId: 2,
    name: "부산 바다 축제",
    isOngoing: false,
    tempMin: null,
    tempMax: null,
    period: "2025.08.01 ~ 2025.08.07",
    hours: "10:00 ~ 20:00",
    phone: "051-111-2222",
    location: "부산광역시 광안리 해수욕장",
    lat: 35.1532,
    lng: 129.1186,
    images: [
      "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1200&q=60",
      "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=60",
    ],
  },
};

function pickDetail(festivalId: FestivalId | undefined): FestivalDetail {
  const key = festivalId === undefined ? "" : String(festivalId);
  if (key && MOCK_FESTIVAL_DETAILS[key]) return MOCK_FESTIVAL_DETAILS[key];

  const first = Object.values(MOCK_FESTIVAL_DETAILS)[0];
  return first ?? {
    festivalId: "unknown",
    name: "(축제명)",
    isOngoing: false,
    tempMin: null,
    tempMax: null,
    period: "(축제 기간)",
    hours: "(운영 시간)",
    phone: "(문의처 전화번호)",
    location: "(위치정보)",
    images: [],
  };
}

export default function ReadPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = (location.state ?? {}) as LocationState;

  const detail = useMemo(() => pickDetail(state.festivalId), [state.festivalId]);

  return (
    <div className="min-h-dvh" style={{ backgroundColor: "var(--c-bg)" }}>
      <Header
        onSearch={(params: NavbarSearchParams) => {
          // 문서 전제: Read에서 검색하면 main으로 이동 + 조건 전달
          navigate("/busanfestival/main", { state: { searchParams: params } });
        }}
      />

      <main className="mx-auto max-w-6xl px-4 py-4 space-y-6 xl:max-w-7xl 2xl:max-w-[90rem]">
        <InfoSection detail={detail} />
        <ImagesSection festivalName={detail.name} images={detail.images} />
        <DirectionsSection detail={detail} />
      </main>
    </div>
  );
}
