import os
import subprocess
import time
import requests
from text_to_audio import text_to_speech_file


def text_to_audio(folder):
    print(f"[TTA] Converting text to audio — {folder}")
    desc_path = f"user_uploads/{folder}/desc.txt"

    if not os.path.exists(desc_path):
        print(f"[TTA] desc.txt nahi mila — skipping")
        return False

    with open(desc_path) as f:
        text = f.read().strip()

    if not text:
        print(f"[TTA] Text empty hai — skipping")
        return False

    text_to_speech_file(text, folder)
    return True


def generate_thumbnail(folder):
    print(f"[THUMB] Generating thumbnail — {folder}")
    base = f"user_uploads/{folder}"

    # Video dhundo
    video_path = None
    for f in os.listdir(base):
        if f.rsplit('.', 1)[-1].lower() in {'mp4', 'mov', 'avi', 'webm'}:
            video_path = f"{base}/{f}"
            break

    # Agar video nahi toh image se thumbnail
    if not video_path:
        for f in os.listdir(base):
            if f.rsplit('.', 1)[-1].lower() in {'jpg', 'jpeg', 'png'}:
                subprocess.run([
                    'ffmpeg', '-i', f"{base}/{f}",
                    '-vf', 'scale=540:960',
                    '-y', f"{base}/thumbnail.jpg"
                ], check=True)
                print(f"[THUMB] Image se thumbnail bana!")
                return

    if video_path:
        subprocess.run([
            'ffmpeg', '-i', video_path,
            '-ss', '00:00:01',
            '-vframes', '1',
            '-y', f"{base}/thumbnail.jpg"
        ], check=True)
        print(f"[THUMB] Video se thumbnail bana!")


def create_reel(folder):
    print(f"[REEL] Creating reel — {folder}")
    base = f"user_uploads/{folder}"

    # Image dhundo
    image_path = None
    for f in os.listdir(base):
        if f.rsplit('.', 1)[-1].lower() in {'jpg', 'jpeg', 'png'}:
            image_path = f"{base}/{f}"
            break

    audio_path = f"{base}/audio.mp3"
    output_path = f"{base}/reel.mp4"

    if not image_path:
        print(f"[REEL] Image nahi mili — skipping")
        return

    if not os.path.exists(audio_path):
        print(f"[REEL] Audio nahi mila — skipping")
        return

    command = [
        'ffmpeg',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-profile:v', 'baseline',
        '-level', '3.0',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        '-vf', 'scale=1080:1920,format=yuv420p',
        '-shortest',
        '-y',
        output_path
    ]

    subprocess.run(command, check=True)
    print(f"[REEL] Reel ready — {output_path}")

    # Thumbnail banao
    generate_thumbnail(folder)

    # Database update karo — thumbnail aur video ready hai
    try:
        res = requests.post(f"http://localhost:5000/update_thumbnail/{folder}")
        if res.status_code == 200:
            print(f"[DB] Database updated for {folder}")
        else:
            print(f"[DB] Update failed: {res.status_code}")
    except Exception as e:
        print(f"[DB] Flask server se connect nahi hua: {e}")


if __name__ == "__main__":
    print("=== Vyakta Processing Queue Started ===")

    while True:
        print("\n[QUEUE] Checking for new uploads...")

        done_folders = []
        if os.path.exists("done.txt"):
            with open("done.txt", "r") as f:
                done_folders = [line.strip() for line in f.readlines()]

        if not os.path.exists("user_uploads"):
            time.sleep(4)
            continue

        folders = os.listdir("user_uploads")

        for folder in folders:
            folder_path = f"user_uploads/{folder}"

            if not os.path.isdir(folder_path):
                continue

            if folder in done_folders:
                continue

            print(f"\n[QUEUE] New folder found: {folder}")

            try:
                # Step 1: Text → Audio
                success = text_to_audio(folder)

                if success:
                    # Step 2: Image + Audio → Reel
                    create_reel(folder)

                # Done mark karo
                with open("done.txt", "a") as f:
                    f.write(folder + "\n")

                print(f"[QUEUE] Done: {folder}")

            except Exception as e:
                print(f"[ERROR] {folder} mein problem: {e}")

        time.sleep(4)