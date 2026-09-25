# 📱 AV-Downloader Mobile (React Native + Expo)

App mobile em **React Native (Expo + TypeScript)** que consome a API `yt-downloader` (`api/main.py`).

## Funcionalidades (espelham o backend)

| UI | Endpoint chamado |
|---|---|
| YouTube único MP4 | `POST /download/video` |
| YouTube único MP3 | `POST /download/audio` |
| YouTube playlist MP4 | `POST /download/playlist/video` |
| YouTube playlist MP3 | `POST /download/playlist/audio` |
| X/Twitter MP4 | `POST /download/x/video` |
| X/Twitter MP3 | `POST /download/x/audio` |

Extras: seletor plataforma/formato/tipo, pasta opcional, colar da área de transferência, health-check `GET /` antes de baixar, feedback de sucesso/erro.

## Pré-requisitos

- Node 18+ / npm
- App **Expo Go** no celular (mesmo Wi-Fi) ou emulador Android
- API rodando: `cd ../api && uvicorn main:app --host 0.0.0.0 --port 8000`

## Configurar URL da API

```bash
cp .env.example .env
# edite EXPO_PUBLIC_API_URL
```

- Emulador Android: `http://10.0.2.2:8000`
- Celular físico: `http://<IP-da-sua-maquina>:8000` (ex.: `http://192.168.1.100:8000`)

## Rodar

```bash
npm install
npm start        # abre o QR Code do Expo
npm run android  # emulador / device Android
npm run ios      # apenas macOS
npm run web      # preview web
```

## Estrutura

```
yt-mobile/
├── App.tsx                  # tela principal (form + download)
├── src/
│   ├── api.ts               # resolveEndpoint + requestDownload + checkHealth
│   ├── theme.ts             # cores (iguais ao yt-front App.css)
│   └── components/
│       └── SegmentedOption.tsx
├── app.json                 # config Expo (slug yt-mobile, android package)
├── package.json             # expo ~53 + react-native 0.79 + TS
└── .env.example
```
