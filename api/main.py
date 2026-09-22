import os
import base64
from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel, HttpUrl 
import yt_dlp

app = FastAPI(
    title="YT-DLP Downloader API", 
    description="API para download de vídeos e aúdios usando yt-dlp", 
    version="1.0.0"
)


def get_download_path() -> str:
    """Retorna o caminho do diretório de downloads."""
    download_path = os.getenv("DOWNLOAD_DIR", "downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    return download_path


DOWNLOAD_DIR = get_download_path()

class DownloadRequest(BaseModel): 
    url: str 
    folder_name: str | None = None

class XDownloadRequest(BaseModel):
    url: str
    folder_name: str | None = None
    cookies: str | None = None  # base64 encoded cookies or file path

def executar_download(url: str, options: dict): 
    try: 
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
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


@app.get("/")
def home(): 
    return {
        "message": "API de Download Ativa", 
        "docs": "Acesse /docs para terstar as rotas interativamente"
    }

@app.post("/download/video")
def download_video(request: DownloadRequest): 
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


@app.post("/download/audio")
def download_audio(req: DownloadRequest): 
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

@app.post('/download/playlist/video')
def download_playlist_video(req: DownloadRequest): 
    pasta = os.path.join(DOWNLOAD_DIR, req.folder_name or "playlists_video/%(playlist_title)s")
    options = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{pasta}/%(playlist_index)s - %(title)s.%(ext)s',
        'noplaylist': False,
    }
    executar_download(req.url, options)
    return {"status": "sucesso", "mensagem": "Playlist de vídeos baixada", "destino": pasta}

@app.post("/download/playlist/audio")
def download_playlist_audio(req: DownloadRequest):
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

@app.post("/download/x/video")
def download_x_video(request: XDownloadRequest):
    """Download de vídeo individual do X (Twitter)."""
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "x_videos")
    options = get_x_options(pasta, request.cookies, is_audio=False)
    executar_download(request.url, options)
    return {
        "status": "success",
        "message": "Vídeo do X baixado com sucesso",
        "destiny": pasta
    }

@app.post("/download/x/audio")
def download_x_audio(request: XDownloadRequest):
    """Download de áudio do X (Twitter)."""
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "x_audio")
    options = get_x_options(pasta, request.cookies, is_audio=True)
    executar_download(request.url, options)
    return {
        "status": "success",
        "message": "Áudio do X baixado com sucesso",
        "destiny": pasta
    }