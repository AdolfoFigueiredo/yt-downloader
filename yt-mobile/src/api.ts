// Cliente HTTP da API yt-downloader (espelha api/main.py)
export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://192.168.1.100:8000";

export type Platform = "youtube" | "x";
export type MediaType = "video" | "audio";
export type PlaylistKind = "single" | "playlist";

export interface DownloadParams {
  url: string;
  folder_name?: string;
  cookies?: string;
}

export interface DownloadResult {
  status: string;
  message?: string;
  mensagem?: string;
  destiny?: string;
  destino?: string;
}

async function post<T>(path: string, body: DownloadParams): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

/** Resolve o endpoint correto conforme plataforma / tipo / playlist. */
export function resolveEndpoint(
  platform: Platform,
  media: MediaType,
  kind: PlaylistKind
): string {
  if (platform === "x") {
    return media === "video" ? "/download/x/video" : "/download/x/audio";
  }
  if (kind === "playlist") {
    return media === "video"
      ? "/download/playlist/video"
      : "/download/playlist/audio";
  }
  return media === "video" ? "/download/video" : "/download/audio";
}

export function requestDownload(
  platform: Platform,
  media: MediaType,
  kind: PlaylistKind,
  params: DownloadParams
): Promise<DownloadResult> {
  return post<DownloadResult>(resolveEndpoint(platform, media, kind), params);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/`);
    return res.ok;
  } catch {
    return false;
  }
}
