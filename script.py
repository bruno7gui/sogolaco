import os
import ffmpeg
from pytube import YouTube
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÕES DE DIRETÓRIOS ---
RAW_DIR = "videos/raw"
EDITED_DIR = "videos/edited"
FONT_PATH = "assets/Montserrat-Bold.ttf"
CRED_PATH = "assets/credenciais.json"  # JSON da conta de serviço

# --- CRIA DIRETÓRIOS SE NECESSÁRIOS ---
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(EDITED_DIR, exist_ok=True)

# --- OBTÉM O PRÓXIMO LINK DA PLANILHA GOOGLE SHEETS ---
def get_next_video_url():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_PATH, scope)
    client = gspread.authorize(creds)

    sheet = client.open("Golaços").sheet1  # nome da planilha
    data = sheet.get_all_records()

    for i, row in enumerate(data):
        if not row.get("usado", "").strip().lower() in ["true", "1", "x"]:
            sheet.update_cell(i + 2, 2, "TRUE")  # marca como usado (coluna 2)
            return row["url"]

    raise Exception("Todos os vídeos já foram usados!")

# --- BAIXA O VÍDEO DO YOUTUBE ---
def baixar_video():
    url = get_next_video_url()
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension='mp4', res="720p").first()
    output_path = os.path.join(RAW_DIR, f"{yt.video_id}.mp4")
    stream.download(output_path=RAW_DIR, filename=f"{yt.video_id}.mp4")
    print(f"[✔] Vídeo baixado: {output_path}")
    return output_path, yt.video_id

# --- ADICIONA TEXTO SOBREPOSTO NO VÍDEO ---
def editar_video(input_video, video_id):
    output_video = os.path.join(EDITED_DIR, f"{video_id}_editado.mp4")
    legenda = "E se existisse uma página só com golaços do futebol?"

    (
        ffmpeg
        .input(input_video)
        .filter("drawtext",
                fontfile=FONT_PATH,
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

    print(f"[✔] Vídeo editado: {output_video}")
    return output_video

# --- EXECUÇÃO PRINCIPAL ---
def main():
    print(f"🚀 Execução iniciada: {datetime.now()}")
    input_path, video_id = baixar_video()
    editar_video(input_path, video_id)
    print(f"✅ Finalizado às {datetime.now()}")

if __name__ == "__main__":
    main()
