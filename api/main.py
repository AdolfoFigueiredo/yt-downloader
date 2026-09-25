import os

import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="YT-DLP Downloader API",
    description="""
    API para download de vídeos e áudios de múltiplas plataformas usando yt-dlp.

    Suporta:
    - YouTube (vídeos e playlists)
    - X/Twitter (vídeos e áudios)
    - Outras plataformas suportadas pelo yt-dlp

    ## Funcionalidades
    - Download de vídeos em MP4 (melhor qualidade)
    - Extração de áudio em MP3 (192kbps)
    - Suporte a playlists
    - Retorno direto do arquivo ao cliente
    """,
    version="2.0.0",
    contact={"name": "API Support"},
)


def get_download_path() -> str:
    """Retorna o caminho do diretório de downloads."""
    download_path = os.getenv("DOWNLOAD_DIR", "downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    return download_path


DOWNLOAD_DIR = get_download_path()

class DownloadRequest(BaseModel):
    """Modelo de requisição para download de vídeo/áudio."""
    url: str = Field(
        ...,
        description="URL do vídeo para download",
        examples=["https://www.youtube.com/watch?v=example"],
    )
    folder_name: str | None = Field(
        None,
        description="Nome da pasta para salvar o arquivo (opcional)",
        examples=["meus_videos"],
    )

class XDownloadRequest(BaseModel):
    url: str
    folder_name: str | None = None
    cookies: str | None = None  # base64 encoded cookies or file path

def executar_download(url: str, options: dict) -> str:
    """Executa o download e retorna o caminho do arquivo baixado."""
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the downloaded filename
            filename = ydl.prepare_filename(info)
            # If postprocessors were used, the extension might change
            if 'postprocessors' in options:
                # For audio extraction, the file might have a different extension
                base, _ = os.path.splitext(filename)
                if options['postprocessors'][0].get('preferredcodec') == 'mp3':
                    filename = base + '.mp3'
            return filename
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_x_options(output_path: str, cookies: str | None = None, is_audio: bool = False) -> dict:
    """Retorna configurações específicas do yt-dlp para X (Twitter)."""
    options = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'noplaylist': True,
    }
    
    if cookies:
        # Se cookies forem fornecidos, tentar usar como arquivo
        options['cookiefile'] = cookies
    
    if is_audio:
        options.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        options.update({
            'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
            'merge_output_format': 'mp4',
        })
    
    return options


@app.get("/", tags=["Health"])
def home():
    """Endpoint de health check para verificar se a API está funcionando."""
    return {
        "message": "API de Download Ativa",
        "docs": "Acesse /docs para testar as rotas interativamente",
        "version": "2.0.0",
    }

@app.post(
    "/download/video",
    tags=["Downloads"],
    summary="Download de vídeo",
    response_description="Arquivo MP4 do vídeo baixado",
)
def download_video(request: DownloadRequest):
    """
    Download de vídeo de qualquer plataforma suportada pelo yt-dlp.

    - **url**: URL do vídeo (YouTube, X/Twitter, etc.)
    - **folder_name**: Nome da pasta para salvar (opcional, padrão: 'videos')

    Retorna o arquivo MP4 diretamente ao cliente.
    """
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "videos")
    options = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'merger_output_format': 'mp4',
        'outtmpl': f'{pasta}/%(title)s.%(ext)s',
        'noplaylist': True
    }
    filename = executar_download(request.url, options)
    return FileResponse(filename)


@app.post(
    "/download/audio",
    tags=["Downloads"],
    summary="Download de áudio",
    response_description="Arquivo MP3 do áudio extraído",
)
def download_audio(req: DownloadRequest):
    """
    Download de áudio de qualquer plataforma suportada pelo yt-dlp.

    - **url**: URL do vídeo (YouTube, X/Twitter, etc.)
    - **folder_name**: Nome da pasta para salvar (opcional, padrão: 'musics')

    Extrai o áudio em MP3 com qualidade de 192kbps e retorna diretamente ao cliente.
    """
    pasta = os.path.join(DOWNLOAD_DIR, req.folder_name or 'musics')
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'outtmpl': f'{pasta}/%(title)s.%(ext)s',
        'noplaylist': True
    }
    filename = executar_download(req.url, options)
    return FileResponse(filename)

@app.post(
    '/download/playlist/video',
    tags=["Playlists"],
    summary="Download de playlist de vídeos",
    response_description="Arquivo MP4 do primeiro vídeo da playlist",
)
def download_playlist_video(req: DownloadRequest):
    """
    Download de playlist de vídeos do YouTube.

    - **url**: URL da playlist do YouTube
    - **folder_name**: Nome da pasta para salvar (opcional)

    Baixa todos os vídeos e retorna o arquivo do primeiro vídeo.
    """
    pasta = os.path.join(DOWNLOAD_DIR, req.folder_name or "playlists_video/%(playlist_title)s")
    options = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{pasta}/%(playlist_index)s - %(title)s.%(ext)s',
        'noplaylist': False,
    }
    filename = executar_download(req.url, options)
    return FileResponse(filename)

@app.post(
    "/download/playlist/audio",
    tags=["Playlists"],
    summary="Download de playlist de áudios",
    response_description="Arquivo MP3 do primeiro áudio da playlist",
)
def download_playlist_audio(req: DownloadRequest):
    """
    Download de playlist de áudios do YouTube.

    - **url**: URL da playlist do YouTube
    - **folder_name**: Nome da pasta para salvar (opcional)

    Extrai os áudios em MP3 e retorna o arquivo do primeiro áudio.
    """
    pasta = os.path.join(DOWNLOAD_DIR, req.folder_name or "playlists_audio/%(playlist_title)s")
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{pasta}/%(playlist_index)s - %(title)s.%(ext)s',
        'noplaylist': False,
    }
    filename = executar_download(req.url, options)
    return FileResponse(filename)

@app.post("/download/x/video")
def download_x_video(request: XDownloadRequest):
    """Download de vídeo individual do X (Twitter)."""
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "x_videos")
    options = get_x_options(pasta, request.cookies, is_audio=False)
    filename = executar_download(request.url, options)
    return FileResponse(filename)

@app.post("/download/x/audio")
def download_x_audio(request: XDownloadRequest):
    """Download de áudio do X (Twitter)."""
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "x_audio")
    options = get_x_options(pasta, request.cookies, is_audio=True)
    filename = executar_download(request.url, options)
    return FileResponse(filename)