import os
import tempfile
import zipfile

import yt_dlp
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    contact={
        "name": "API Support",
    }
)

# Permite que um frontend acessado em outro PC consuma a API.
# Em produção, restrinja os domínios separando por vírgula na variável CORS_ORIGINS.
origens_cors = [origem.strip() for origem in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_cors,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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

class XDownloadRequest(BaseModel):
    """Modelo de requisição para download do X (Twitter)."""
    url: str = Field(..., description="URL do vídeo do X (Twitter)", examples=["https://x.com/usuario/status/123456789"])
    folder_name: str | None = Field(None, description="Nome da pasta para salvar o arquivo (opcional, padrão: 'x_videos' ou 'x_audio')", examples=["meus_x_videos"])
    cookies: str | None = Field(None, description="Caminho do arquivo de cookies para conteúdo privado (opcional)", examples=["/path/to/cookies.txt"])

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


def compactar_pasta(pasta: str) -> str:
    """Cria um ZIP com todos os arquivos baixados e retorna seu caminho."""
    arquivo = tempfile.NamedTemporaryFile(prefix="yt-playlist-", suffix=".zip", delete=False)
    caminho_zip = arquivo.name
    arquivo.close()

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as pacote:
        for diretorio, _, arquivos in os.walk(pasta):
            for nome in arquivos:
                origem = os.path.join(diretorio, nome)
                pacote.write(origem, os.path.relpath(origem, pasta))

    return caminho_zip


def baixar_playlist_para_zip(url: str, formato: str, background_tasks: BackgroundTasks) -> FileResponse:
    """Baixa uma playlist em uma pasta temporária e a retorna como ZIP."""
    with tempfile.TemporaryDirectory(prefix="yt-playlist-") as pasta:
        if formato == "audio":
            options = {
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            nome_zip = "playlist_audio.zip"
        else:
            options = {
                "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
                "merge_output_format": "mp4",
            }
            nome_zip = "playlist_video.zip"

        options.update({
            "outtmpl": os.path.join(pasta, "%(playlist_index)s - %(title)s.%(ext)s"),
            "noplaylist": False,
        })
        executar_download(url, options)
        caminho_zip = compactar_pasta(pasta)

    background_tasks.add_task(os.remove, caminho_zip)
    return FileResponse(
        caminho_zip,
        media_type="application/zip",
        filename=nome_zip,
        background=background_tasks,
    )


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

@app.post(
    '/download/playlist/video',
    tags=["Playlists"],
    summary="Download de playlist de vídeos",
    response_description="Arquivo ZIP com todos os vídeos da playlist",
)
def download_playlist_video(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Baixa todos os vídeos e retorna um ZIP para o cliente."""
    return baixar_playlist_para_zip(req.url, "video", background_tasks)

@app.post(
    "/download/playlist/audio",
    tags=["Playlists"],
    summary="Download de playlist de áudios",
    response_description="Arquivo ZIP com todos os áudios da playlist",
)
def download_playlist_audio(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Baixa todos os áudios e retorna um ZIP para o cliente."""
    return baixar_playlist_para_zip(req.url, "audio", background_tasks)

@app.post("/download/x/video", tags=["X/Twitter"], summary="Download de vídeo do X (Twitter)", response_description="Arquivo MP4 do vídeo do X baixado")
def download_x_video(request: XDownloadRequest):
    """
    Download de vídeo do X (Twitter).

    - **url**: URL do vídeo do X (Twitter)
    - **folder_name**: Nome da pasta para salvar (opcional, padrão: 'x_videos')
    - **cookies**: Caminho do arquivo de cookies para conteúdo privado (opcional)

    Retorna o arquivo MP4 diretamente ao cliente.
    """
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "x_videos")
    options = get_x_options(pasta, request.cookies, is_audio=False)
    executar_download(request.url, options)
    return {
        "status": "success",
        "message": "Vídeo do X baixado com sucesso",
        "destiny": pasta
    }

@app.post("/download/x/audio", tags=["X/Twitter"], summary="Download de áudio do X (Twitter)", response_description="Arquivo MP3 do áudio do X extraído")
def download_x_audio(request: XDownloadRequest):
    """
    Download de áudio do X (Twitter).

    - **url**: URL do vídeo do X (Twitter)
    - **folder_name**: Nome da pasta para salvar (opcional, padrão: 'x_audio')
    - **cookies**: Caminho do arquivo de cookies para conteúdo privado (opcional)

    Extrai o áudio em MP3 com qualidade de 192kbps e retorna diretamente ao cliente.
    """
    pasta = os.path.join(DOWNLOAD_DIR, request.folder_name or "x_audio")
    options = get_x_options(pasta, request.cookies, is_audio=True)
    executar_download(request.url, options)
    return {
        "status": "success",
        "message": "Áudio do X baixado com sucesso",
        "destiny": pasta
    }