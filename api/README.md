# 🚀 YT-DLP Async Downloader API

Uma API assíncrona e containerizada construída com **FastAPI** e **yt-dlp** para realizar downloads de vídeos e áudios (MP3) do YouTube (individuais ou playlists), com acompanhamento de progresso em tempo real no navegador.

---

## Funcionalidades

- **Downloads Assíncronos:** O processamento roda em segundo plano com `BackgroundTasks`, permitindo respostas instantâneas da API.
- **Acompanhamento em Tempo Real:** Interface web nativa (`/view/{task_id}`) com barra de progresso, velocidade de download e tempo estimado (ETA).
- **Suporte Multi-formato:**
  - Vídeo na melhor qualidade combinada (MP4).
  - Extração de áudio em MP3 (192 kbps).
- **Suporte a Playlists:** Organização automática com índices de vídeos e subpastas personalizadas.
- **Ambiente Plug & Play (Docker):** Suporte nativo a FFmpeg e isolamento total via Docker Compose.

---

## Tecnologias Utilizadas

- **Python 3.11**
- **FastAPI** & **Uvicorn**
- **yt-dlp**
- **FFmpeg**
- **Docker** & **Docker Compose**

---

## Como Executar (Plug & Play com Docker)

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### Passo a Passo

1. Suba o container com o Docker Compose:
   ```bash
   docker compose up -d

2. Acesse a documentação interatva da aPI no seu navegador:
    
    Swagger UI:
    ```bash
    http://localhost:8000/docs

Todos os Dowloads são sincronizados diretamente com o seu sistema host na pasta `~/Downloads/yt-api`


## Execução Local(Sem Docker)
### Pré-Requisitos
 - [ffmpeg] ()
 - [python3.14+] ()


### Passo a passo
1. Criar e ativar o ambiente virtual 
    ```bash 
    python -m venv venv
    source venv/bin/activate.fish
2. Instalar as dependências
    ```bash
    pip install -r requirements.txt
3. Iniciar o servidor
    ```bahs 
    uvicorn main:app --reload`


## Endpoints da API

### Download de Vídeos do X (Twitter)

#### POST `/download/x/video`
Download de vídeo individual do X (Twitter).

**Parâmetros:**
- `url` (obrigatório): URL do vídeo do X
- `folder_name` (opcional): Nome da pasta para salvar o vídeo
- `cookies` (opcional): Caminho do arquivo de cookies para conteúdo privado

**Exemplo de uso:**
```json
{
  "url": "https://x.com/usuario/status/123456789",
  "folder_name": "meus_videos_x"
}
```

#### POST `/download/x/audio`
Download de áudio do X (Twitter).

**Parâmetros:**
- `url` (obrigatório): URL do vídeo do X
- `folder_name` (opcional): Nome da pasta para salvar o áudio
- `cookies` (opcional): Caminho do arquivo de cookies para conteúdo privado

**Exemplo de uso:**
```json
{
  "url": "https://x.com/usuario/status/123456789",
  "folder_name": "meus_audios_x"
}
```

**Como obter cookies do X:**
1. Faça login no X (Twitter) no seu navegador
2. Instale uma extensão como "Get cookies.txt LOCALLY" ou "EditThisCookie"
3. Exporte os cookies do domínio x.com
4. Salve o arquivo e use o caminho no parâmetro `cookies`

### Download de playlist para o PC do cliente

Os endpoints de playlist retornam um arquivo ZIP para o computador que fez a requisição:

- `POST /download/playlist/video` — `playlist_video.zip`
- `POST /download/playlist/audio` — `playlist_audio.zip`

Exemplo de requisição:

```bash
curl -X POST "http://IP_DO_SERVIDOR:8000/download/playlist/video" \\
  -H "Content-Type: application/json" \\
  -d '{"url":"https://www.youtube.com/playlist?list=ID_DA_PLAYLIST"}' \\
  -o playlist_video.zip
```

Para que outros computadores na rede local acessem a API, inicie o Uvicorn escutando todas as interfaces:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

No Docker Compose, a porta `8000` já está publicada. Consulte a documentação em `http://IP_DO_SERVIDOR:8000/docs`.

As playlists são baixadas temporariamente no servidor, compactadas em ZIP e removidas depois do envio. O servidor precisa ter `ffmpeg` instalado para merger de vídeo e conversão de áudio.

### Outros Endpoints 
