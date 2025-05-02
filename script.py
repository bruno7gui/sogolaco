import os
from instagrapi import Client
from datetime import datetime
import ffmpeg
import yt_dlp

# --- VARIÁVEIS DE AMBIENTE ---
IG_USER = os.getenv("INSTAGRAM_USER")
IG_PASS = os.getenv("INSTAGRAM_PASS")

# --- 1. BAIXAR UM VÍDEO DE GOLAÇO ---
def baixar_video_youtube(link, output_path):
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# --- 2. EDITAR O VÍDEO COM INTRO E TEXTO ---
def editar_video(input_video, output_video):
    legenda = "E se existisse uma página só com golaços do futebol?"
    fonte = "assets/font.ttf"  # Se quiser usar uma fonte específica

    (
        ffmpeg
        .input(input_video)
        .filter("drawtext",
                fontfile=fonte,
                text=legenda,
                fontcolor='white',
                fontsize=48,
                x='(w-text_w)/2',
                y='h-100',
                box=1,
                boxcolor='black@0.5',
                boxborderw=10)
        .output(output_video)
        .run(overwrite_output=True)
    )

# --- 3. POSTAR NO INSTAGRAM ---
def postar_instagram(caminho_video):
    cl = Client()
    cl.login(IG_USER, IG_PASS)

    legenda = "E se existisse uma página só com golaços do futebol? ⚽🔥\n\n#futebol #golaço #soccer"
    cl.clip_upload(caminho_video, legenda)

# --- EXECUÇÃO COMPLETA ---
if __name__ == "__main__":
    yt_link = "https://www.youtube.com/watch?v=gzrKQuJAPSE"  # <- substitua por um link válido
    raw_video = "videos/raw/golaco.mp4"
    final_video = f"videos/edited/golaco_{datetime.now().strftime('%H%M')}.mp4"

    baixar_video_youtube(yt_link, raw_video)
    editar_video(raw_video, final_video)
    postar_instagram(final_video)

