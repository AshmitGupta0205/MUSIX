import streamlit as st
import os
import subprocess
import shlex
import yt_dlp
import sounddevice as sd
import soundfile as sf
import numpy as np
import librosa
from datetime import datetime

# Define directories
UPLOAD_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SEPARATED_DIR = "separated"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(SEPARATED_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---- UI Setup ----
st.set_page_config(page_title="🎤 AI Karaoke Maker", page_icon="🎶", layout="wide")
st.title("🎤 AI Karaoke Maker")
st.write("Fetch a song, separate vocals, record your voice, and create a karaoke track!")

# Sidebar Navigation
st.sidebar.header("Navigation")
if st.sidebar.button("🏠 Back to Home", key="sidebar_home"):
    subprocess.Popen(["streamlit", "run", "app.py"])
    st.stop()

# Function to check if input is a YouTube URL
def is_youtube_url(input_text):
    return "youtube.com" in input_text or "youtu.be" in input_text

# Function to download from YouTube
def download_youtube_audio(search_query):
    if not is_youtube_url(search_query):
        search_query = f"ytsearch1:{search_query}"
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "noplaylist": True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(search_query, download=True)
            downloaded_file = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            return downloaded_file
        except Exception as e:
            st.error(f"❌ Error downloading: {e}")
            return None

# User input for YouTube URL or Song Name
search_input = st.text_input("🎶 Enter YouTube URL or Song Name")
file_path = None

if search_input and st.button("⬇️ Fetch & Download"):
    st.info("⏳ Fetching audio from YouTube...")
    downloaded_file_path = download_youtube_audio(search_input)
    if downloaded_file_path and os.path.exists(downloaded_file_path):
        file_path = downloaded_file_path
        st.success(f"✅ Downloaded: {os.path.basename(downloaded_file_path)}")

# File Upload Feature
uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])
if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File uploaded: {uploaded_file.name}")

if file_path and os.path.exists(file_path):
    st.write(f"📂 Selected file: {os.path.basename(file_path)}")
    
    # Extract song duration
    duration = librosa.get_duration(filename=file_path)
    st.write(f"⏳ Song duration: {duration:.2f} seconds")
    
    # Separation Options
    stem_choice = "2 stems (Vocals + Instrumental)"  # Fixed to 2 stems since karaoke only needs instrumentals

    if st.button("🎵 Separate Audio"):
        st.info("⏳ Processing... This may take a while.")
        output_folder = os.path.join(SEPARATED_DIR)
        os.makedirs(output_folder, exist_ok=True)
        
        demucs_command = f"demucs --two-stems vocals -o {output_folder} {shlex.quote(file_path)}"
        process = subprocess.run(demucs_command, shell=True, text=True, capture_output=True)
        
        if process.returncode == 0:
            st.success("✅ Separation complete! Proceed to recording.")
        else:
            st.error("❌ Demucs error! Check logs for details.")

# Karaoke Recording Feature
st.header("🎤 Karaoke Recorder")

if file_path:
    song_name = os.path.splitext(os.path.basename(file_path))[0]
    instrumental_path = None
    instrumental_folder = os.path.join(SEPARATED_DIR, "htdemucs", song_name)
    if os.path.exists(instrumental_folder):
        for file in os.listdir(instrumental_folder):
            if "no_vocals" in file or "instrumental" in file:
                instrumental_path = os.path.join(instrumental_folder, file)
                break
    
    if instrumental_path:
        st.audio(instrumental_path, format='audio/mp3')
        instrumental_duration = librosa.get_duration(filename=instrumental_path)
        st.write(f"🎵 Instrumental Duration: {instrumental_duration:.2f} seconds")

        if st.button("🎙️ Start Recording"):
            st.info("🎙️ Recording... Speak into the microphone!")
            samplerate = 44100
            recording = sd.rec(int(instrumental_duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
            sd.wait()
            
            recorded_voice_path = os.path.join(RESULTS_DIR, f"{song_name}_recorded.wav")
            sf.write(recorded_voice_path, recording, samplerate)
            st.success("✅ Recording complete!")
            
            # Add timestamp to avoid overwriting
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_karaoke_path = os.path.join(RESULTS_DIR, f"{song_name}_karaoke_{timestamp}.wav")
            
            # Merge Instrumental and Voice with adjusted volumes
            merge_command = f"ffmpeg -i {shlex.quote(instrumental_path)} -i {shlex.quote(recorded_voice_path)} -filter_complex '[0:a]volume=0.7[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2' {shlex.quote(final_karaoke_path)}"
            subprocess.run(merge_command, shell=True)
            
            if os.path.exists(final_karaoke_path):
                st.success("✅ Karaoke track created!")
                st.audio(final_karaoke_path, format='audio/wav')
                with open(final_karaoke_path, "rb") as f:
                    st.download_button("⬇️ Download Karaoke Track", f, file_name=os.path.basename(final_karaoke_path))

# "Back to Home" Button
st.markdown("---")
if st.button("🏠 Back to Home", key="main_home"):
    subprocess.Popen(["streamlit", "run", "app.py"])
    st.stop()