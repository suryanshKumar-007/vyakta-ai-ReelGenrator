import os
from gtts import gTTS


def text_to_speech_file(text: str, folder: str) -> str:
    save_file_path = os.path.join(f"user_uploads/{folder}", "audio.mp3")

    tts = gTTS(text=text, lang='en')
    tts.save(save_file_path)

    print(f"{save_file_path}: Audio saved successfully!")
    return save_file_path


# Test karne ke liye uncomment kar:
# text_to_speech_file("Hey I am Suryansh and this is the Vyakta project", "test-folder")