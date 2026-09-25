import * as FileSystem from "expo-file-system/legacy";
import * as Sharing from "expo-sharing";

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

function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunkSize = 0x8000;
  for (let inicio = 0; inicio < bytes.length; inicio += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(inicio, inicio + chunkSize));
  }
  return globalThis.btoa(binary);
}

async function postPlaylistZip(path: string, body: DownloadParams): Promise<DownloadResult> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }

  const filename = path.endsWith("/audio") ? "playlist_audio.zip" : "playlist_video.zip";
  const destino = `${FileSystem.cacheDirectory}${filename}`;
  const base64 = arrayBufferToBase64(await res.arrayBuffer());
  await FileSystem.writeAsStringAsync(destino, base64, {
    encoding: FileSystem.EncodingType.Base64,
  });
  await Sharing.shareAsync(destino, {
    dialogTitle: "Salvar playlist",
    mimeType: "application/zip",
    UTI: "public.zip-archive",
  });

  return {
    status: "success",
    message: "Playlist salva. Escolha onde guardar o arquivo ZIP.",
    destiny: destino,
  };
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
  const path = resolveEndpoint(platform, media, kind);
  if (platform === "youtube" && kind === "playlist") {
    return postPlaylistZip(path, params);
  }
  return post<DownloadResult>(path, params);
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/`);
    return res.ok;
  } catch {
    return false;
  }
}
