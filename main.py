import tkinter as tk
from tkinter import filedialog, messagebox
import openai
from dotenv import load_dotenv
import os
import platform
import subprocess

# Загрузка API-ключа OpenAI из .env файла
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Получение пути к рабочему столу в зависимости от ОС
def get_desktop_path():
    if platform.system() == "Windows":
        return os.path.join(os.environ['USERPROFILE'], 'Desktop')
    else:
        return os.path.join(os.path.expanduser('~'), 'Desktop')

# Функция для конвертации аудиофайла с Whisper
def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            # Отображение сообщения об отправке в нейросеть
            result_label.config(text="Отправка в нейромир...")
            root.update_idletasks()  # Обновление интерфейса для отображения сообщения
            
            # Запрос к OpenAI API
            transcription = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return transcription['text']
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при конвертации: {e}")
        return None

# Функция для открытия файла после конвертации
def open_file(filepath):
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(('open', filepath))
    else:  # Linux
        subprocess.call(('xdg-open', filepath))

# Функция для выбора файла и его конвертации
def choose_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.mp3 *.wav *.m4a")]
    )
    
    if file_path:
        result_label.config(text="Идёт конвертация...")
        transcription_text = transcribe_audio(file_path)
        if transcription_text is None:
            result_label.config(text="Ошибка конвертации.")
            return
        
        # Сохранение результата конвертации на рабочий стол
        desktop_path = get_desktop_path()
        output_file_path = os.path.join(desktop_path, "CONVERTED.txt")
        with open(output_file_path, "w") as output_file:
            output_file.write("конвертация:\n")
            output_file.write(transcription_text)
        
        result_label.config(text="Обработка завершена! Результат сохранён на рабочем столе.")
        
        # Открытие файла после сохранения
        open_file(output_file_path)

# Настройка окна
root = tk.Tk()
root.title("Конвертер аудио в текст")
root.geometry("500x300")

# Надпись заголовка
title_label = tk.Label(root, text="Выберите аудиофайл для конвертации", font=("Arial", 14))
title_label.pack(pady=10)

# Кнопка для выбора файла и начала конвертации
transcribe_button = tk.Button(root, text="Аудио->Текст", font=("Arial", 12), command=choose_file)
transcribe_button.pack(pady=10)

# Метка для вывода результата
result_label = tk.Label(root, text="Development by MaxXx", font=("Arial", 12))
result_label.pack(pady=20)

# Запуск основного цикла приложения
root.mainloop()
