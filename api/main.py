import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, Field
import yt_dlp

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
    contact={
        "name": "API Support",
    }
)


def get_download_path() -> str: 
    """Retorna o caminho do diretório de downloads."""
    download_path = os.getenv("DOWNLOAD_PATH", "downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    return download_path


DOWNLOAD_DIR = get_download_path()

class DownloadRequest(BaseModel):
    """Modelo de requisição para download de vídeo/áudio."""
    url: str = Field(..., description="URL do vídeo para download", examples=["https://www.youtube.com/watch?v=example"])
    folder_name: str | None = Field(None, description="Nome da pasta para salvar o arquivo (opcional)", examples=["meus_videos"])

def executar_download(url: str, options: dict): 
    try: 
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Health"])
def home():
    """Endpoint de health check para verificar se a API está funcionando."""
    return {
        "message": "API de Download Ativa",
        "docs": "Acesse /docs para testar as rotas interativamente",
        "version": "2.0.0"
    }

@app.post("/download/video", tags=["Downloads"], summary="Download de vídeo", response_description="Arquivo MP4 do vídeo baixado")
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
    executar_download(request.url, options)
    return {
        "status": "success",
        "message": 'Video baixado',
        "destiny": pasta
    }


@app.post("/download/audio", tags=["Downloads"], summary="Download de áudio", response_description="Arquivo MP3 do áudio extraído")
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
    executar_download(req.url, options)
    return {
        "status": "success",
        "message": "Áudio baixado",
        "destiny": pasta
    }

@app.post('/download/playlist/video', tags=["Playlists"], summary="Download de playlist de vídeos", response_description="Arquivo MP4 do primeiro vídeo da playlist")
def download_playlist_video(req: DownloadRequest):
    """
    Download de playlist de vídeos do YouTube.

    - **url**: URL da playlist do YouTube
    - **folder_name**: Nome da pasta para salvar (opcional, padrão: 'playlists_video/{playlist_title}')

    Baixa todos os vídeos da playlist. Retorna o arquivo do primeiro vídeo.
    Os arquivos são organizados com índice e título.
    """
    pasta = os.path.join(DOWNLOAD_DIR, req.folder_name or "playlists_video/%(playlist_title)s")
    options = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{pasta}/%(playlist_index)s - %(title)s.%(ext)s',
        'noplaylist': False,
    }
    executar_download(req.url, options)
    return {"status": "sucesso", "mensagem": "Playlist de vídeos baixada", "destino": pasta}

@app.post("/download/playlist/audio", tags=["Playlists"], summary="Download de playlist de áudios", response_description="Arquivo MP3 do primeiro áudio da playlist")
def download_playlist_audio(req: DownloadRequest):
    """
    Download de playlist de áudios do YouTube.

    - **url**: URL da playlist do YouTube
    - **folder_name**: Nome da pasta para salvar (opcional, padrão: 'playlists_audio/{playlist_title}')

    Extrai o áudio de todos os vídeos da playlist em MP3 (192kbps).
    Retorna o arquivo do primeiro áudio. Os arquivos são organizados com índice e título.
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
    executar_download(req.url, options)
    return {"status": "sucesso", "mensagem": "Playlist de áudio baixada", "destino": pasta}