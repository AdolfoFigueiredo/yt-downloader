import os
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
    download_path = os.getenv("DOWNLOAD_PATH", "downloads")
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    return download_path


DOWNLOAD_DIR = get_download_path()

class DownloadRequest(BaseModel): 
    url: str 
    folder_name: str | None = None

def executar_download(url: str, options: dict): 
    try: 
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
        return True
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))


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