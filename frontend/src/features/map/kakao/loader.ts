import "./types";

let kakaoMapsLoadPromise: Promise<void> | null = null;

type LoadOptions = {
  appKey: string;
  libraries?: Array<"services" | "clusterer" | "drawing">;
};

const SCRIPT_ID = "kakao-maps-sdk";

export function loadKakaoMapsSDK(options: LoadOptions): Promise<void> {
  if (typeof window === "undefined") return Promise.reject(new Error("Browser only"));

  // 이미 로드된 경우
  if (window.kakao?.maps) return Promise.resolve();

  // 중복 로드 방지
  if (kakaoMapsLoadPromise) return kakaoMapsLoadPromise;

  const { appKey, libraries = [] } = options;
  if (!appKey) {
    return Promise.reject(new Error("Missing Kakao Maps JavaScript appKey"));
  }

  kakaoMapsLoadPromise = new Promise<void>((resolve, reject) => {
    // 이미 script tag가 있으면 onload만 연결
    const existing = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null;
    if (existing) {
      existing.addEventListener("load", () => {
        if (!window.kakao?.maps) return reject(new Error("Kakao Maps SDK loaded but window.kakao.maps is missing"));
        window.kakao.maps.load(() => resolve());
      });
      existing.addEventListener("error", () => reject(new Error("Failed to load Kakao Maps SDK")));
      return;
    }

    const script = document.createElement("script");
    script.id = SCRIPT_ID;

    const libQuery = libraries.length ? `&libraries=${libraries.join(",")}` : "";
    // 동적 로딩 시 autoload=false + kakao.maps.load 필요 :contentReference[oaicite:9]{index=9}
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${encodeURIComponent(appKey)}&autoload=false${libQuery}`;
    script.async = true;

    script.onload = () => {
      if (!window.kakao?.maps) return reject(new Error("Kakao Maps SDK loaded but window.kakao.maps is missing"));
      window.kakao.maps.load(() => resolve());
    };
    script.onerror = () => reject(new Error("Failed to load Kakao Maps SDK"));

    document.head.appendChild(script);
  });

  return kakaoMapsLoadPromise;
}
