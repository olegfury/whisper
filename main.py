import os
import tkinter as tk
from tkinter import filedialog
import whisper
from pyannote.audio import Pipeline
import ffmpeg
import shutil
import threading

from dotenv import load_dotenv
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Инициализация модели диаризации
diarization_model = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)

# Функция для конвертации MP3 в WAV
def convert_to_wav(input_file):
    output_file = "temp.wav"
    try:
        if os.path.exists(output_file):
            os.remove(output_file)
        (
            ffmpeg
            .input(input_file)
            .output(output_file)
            .run(overwrite_output=True)
        )
        return output_file
    except Exception as e:
        status_label.config(text=f"Ошибка при конвертации: {e}")
        return None

# Функция для обработки аудио
def process_audio(file_path, model_size):
    status_label.config(text="Конвертация MP3 в WAV...")
    root.update_idletasks()
    
    wav_file = convert_to_wav(file_path)
    if wav_file is None:
        return
    
    try:
        # Whisper для транскрипции
        status_label.config(text="Запуск Whisper для транскрипции...")
        root.update_idletasks()
        model = whisper.load_model(model_size)
        result = model.transcribe(wav_file, verbose=True)
        
        # Путь к рабочему столу
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

        # Сохраняем результат Whisper на рабочий стол
        whisper_output_file = os.path.join(desktop_path, "whisper_transcription.txt")
        with open(whisper_output_file, "w", encoding="utf-8") as whisper_file:
            whisper_file.write(result["text"])
        
        # Выполняем диаризацию
        status_label.config(text="Диаризация...")
        root.update_idletasks()
        diarization = diarization_model(wav_file)
        
        # Сохраняем результат диаризации на рабочий стол
        diarization_output_file = os.path.join(desktop_path, "diarized_transcription.txt")
        with open(diarization_output_file, "w", encoding="utf-8") as diarization_file:
            segments = result["segments"]
            for segment in segments:
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"]
                
                # Ищем спикера для этого сегмента
                speaker = None
                for speech_segment, _, spkr in diarization.itertracks(yield_label=True):
                    if speech_segment.start <= start_time <= speech_segment.end:
                        speaker = spkr
                        break
                
                if speaker is None:
                    speaker = "Unknown"
                
                diarization_file.write(f"{speaker}: {start_time:.1f}-{end_time:.1f}: {text}\n")
        
        status_label.config(text="Обработка завершена. Файлы сохранены на рабочий стол.")
    except Exception as e:
        status_label.config(text=f"Ошибка при выполнении диаризации: {e}")
    finally:
        if os.path.exists(wav_file):
            os.remove(wav_file)

# Функция для выполнения обработки в отдельном потоке
def process_audio_thread(file_path, model_size):
    threading.Thread(target=process_audio, args=(file_path, model_size)).start()

# Выбор файла и запуск обработки
def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        model_size = model_var.get()
        process_audio_thread(file_path, model_size)

# Настройка интерфейса Tkinter
root = tk.Tk()
root.title("Аудио процессор")

# Кнопка для выбора файла
select_button = tk.Button(root, text="Выбрать аудиофайл", command=select_file)
select_button.pack(pady=10)

# Статус выполнения
status_label = tk.Label(root, text="Ожидание выбора файла...")
status_label.pack(pady=10)

# Выбор модели Whisper
model_var = tk.StringVar(value="large")
tk.Label(root, text="Выберите размер модели Whisper:").pack()
tk.Radiobutton(root, text="small", variable=model_var, value="small").pack()
tk.Radiobutton(root, text="medium", variable=model_var, value="medium").pack()
tk.Radiobutton(root, text="large", variable=model_var, value="large-v3").pack()

# Запуск интерфейса
root.mainloop()
