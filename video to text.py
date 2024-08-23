
import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
import os

def select_video_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if file_path:
        video_path.set(file_path)
        transcribe_video(file_path)

def transcribe_video(file_path):
    try:
        # Extract audio from the video
        video_clip = VideoFileClip(file_path)
        audio_path = "temp_audio.wav"
        video_clip.audio.write_audiofile(audio_path)

        # Load audio and transcribe in chunks if necessary
        recognizer = sr.Recognizer()
        audio = AudioSegment.from_wav(audio_path)
        
        # Adjust chunk length to handle longer videos better
        chunk_length_ms = 300000  # 5 minutes chunks
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        
        full_text = ""
        for i, chunk in enumerate(chunks):
            chunk_path = f"temp_chunk_{i}.wav"
            chunk.export(chunk_path, format="wav")
            with sr.AudioFile(chunk_path) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    full_text += text + " "
                except sr.UnknownValueError:
                    # Handle case where speech was unintelligible
                    full_text += "[Unrecognizable speech] "
                except sr.RequestError:
                    # Handle case where API request failed
                    messagebox.showerror("API Error", "API request failed. Please check your internet connection.")
                    return

            os.remove(chunk_path)

        # Display the transcription
        transcription_text.delete("1.0", tk.END)
        transcription_text.insert(tk.END, full_text.strip())

        # Clean up temporary files
        os.remove(audio_path)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Video to Text Converter")

# Path to the selected video file
video_path = tk.StringVar()

# Button to select video file
select_button = tk.Button(root, text="Select MP4 Video File", command=select_video_file)
select_button.pack(pady=20)

# Text widget to display transcription
transcription_text = tk.Text(root, wrap="word", height=20, width=60)
transcription_text.pack(padx=10, pady=10)

# Run the GUI loop
root.mainloop()
