# 🚀 YT-DLP Downloader API

Uma API containerizada construída com **FastAPI** e **yt-dlp** para realizar downloads de vídeos e áudios (MP3) de diversas plataformas (YouTube, X/Twitter, etc.), com retorno direto do arquivo para o cliente.

---

## Funcionalidades

- **Downloads de Vídeo e Áudio:** Suporte a múltiplas plataformas incluindo YouTube e X (Twitter).
- **Retorno Direto do Arquivo:** O arquivo baixado é enviado diretamente ao cliente via HTTP.
- **Suporte Multi-formato:**
  - Vídeo na melhor qualidade combinada (MP4).
  - Extração de áudio em MP3 (192 kbps).
- **Suporte a Playlists:** Organização automática com índices de vídeos e subpastas personalizadas.
- **Suporte ao X (Twitter):** Endpoints específicos com autenticação opcional via cookies.
- **Armazenamento Local:** Arquivos salvos na pasta `downloads/` do projeto.
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

Todos os downloads são salvos na pasta `downloads/` do projeto.


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
Download de vídeo individual do X (Twitter). Retorna o arquivo MP4 diretamente.

**Parâmetros:**
- `url` (obrigatório): URL do vídeo do X
- `folder_name` (opcional): Nome da pasta para salvar o vídeo (padrão: `x_videos`)
- `cookies` (opcional): Caminho do arquivo de cookies para conteúdo privado

**Exemplo de uso:**
```json
{
  "url": "https://x.com/usuario/status/123456789",
  "folder_name": "meus_videos_x"
}
```

#### POST `/download/x/audio`
Download de áudio do X (Twitter). Retorna o arquivo MP3 diretamente.

**Parâmetros:**
- `url` (obrigatório): URL do vídeo do X
- `folder_name` (opcional): Nome da pasta para salvar o áudio (padrão: `x_audio`)
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

### Endpoints Gerais

#### POST `/download/video`
Download de vídeo de qualquer plataforma suportada pelo yt-dlp. Retorna o arquivo MP4 diretamente.

**Parâmetros:**
- `url` (obrigatório): URL do vídeo
- `folder_name` (opcional): Nome da pasta para salvar o vídeo (padrão: `videos`)

#### POST `/download/audio`
Download de áudio de qualquer plataforma suportada pelo yt-dlp. Retorna o arquivo MP3 diretamente.

**Parâmetros:**
- `url` (obrigatório): URL do vídeo
- `folder_name` (opcional): Nome da pasta para salvar o áudio (padrão: `musics`)

#### POST `/download/playlist/video`
Download de playlist de vídeos. Retorna o arquivo do primeiro vídeo diretamente.

**Parâmetros:**
- `url` (obrigatório): URL da playlist
- `folder_name` (opcional): Nome da pasta para salvar a playlist (padrão: `playlists_video/{playlist_title}`)

#### POST `/download/playlist/audio`
Download de playlist de áudios. Retorna o arquivo do primeiro áudio diretamente.

**Parâmetros:**
- `url` (obrigatório): URL da playlist
- `folder_name` (opcional): Nome da pasta para salvar a playlist (padrão: `playlists_audio/{playlist_title}`) 
