import streamlit as st
import os
import subprocess
import shlex
import yt_dlp
import platform
import json

def get_audio_duration(file_path):
    """Gets the duration of an audio file using ffprobe."""
    command = f"ffprobe -i {shlex.quote(file_path)} -show_entries format=duration -v quiet -of json"
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        duration_info = json.loads(result.stdout)
        return float(duration_info["format"]["duration"]) if "format" in duration_info else None
    except Exception as e:
        st.error(f"❌ Error getting duration: {e}")
        return None

def list_audio_devices():
    """Lists available audio input devices and returns them as a dictionary."""
    system_os = platform.system()
    devices = {}
    
    if system_os == "Darwin":  # macOS
        result = subprocess.run(["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""], 
                                capture_output=True, text=True)
        lines = result.stderr.split("\n")
        for line in lines:
            if "AVFoundation audio devices:" in line or not line.strip():
                continue
            if "]" in line:
                index, name = line.split("] ", 1)
                devices[index.strip(" [")] = name.strip()
    
    elif system_os == "Windows":
        result = subprocess.run(["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
                                capture_output=True, text=True, shell=True)
        lines = result.stderr.split("\n")
        for line in lines:
            if "DirectShow audio devices" in line or not line.strip():
                continue
            if "]" in line:
                index, name = line.split("] ", 1)
                devices[index.strip(" [")] = name.strip()
    
    return devices

def get_ffmpeg_audio_device(selected_device):
    """Returns the appropriate FFmpeg command for the selected device."""
    system_os = platform.system()
    
    if system_os == "Darwin":
        return "avfoundation", f":{selected_device}"
    elif system_os == "Windows":
        return "dshow", f"audio={selected_device}"
    else:
        raise ValueError("❌ Unsupported OS for recording!")

# Define directories
UPLOAD_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SEPARATED_DIR = "separated"
RESULTS_DIR = "results"

for directory in [UPLOAD_DIR, DOWNLOADS_DIR, SEPARATED_DIR, RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

st.set_page_config(page_title="AI Karaoke Maker", page_icon="🎶", layout="wide")
st.title("🎤 AI Karaoke Maker")
st.write("Fetch a song, separate vocals, record your voice, and create a karaoke track!")

devices = list_audio_devices()
selected_device = st.selectbox("🎙 Select Audio Device", options=list(devices.values()))

devices_reversed = {v: k for k, v in devices.items()}
selected_device_index = devices_reversed.get(selected_device, "0")

search_input = st.text_input("🎶 Enter YouTube URL or Song Name")
file_path = None

if search_input and st.button("⬇️ Fetch & Download"):
    st.info("⏳ Fetching audio from YouTube...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(search_input, download=True)
            downloaded_file = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            file_path = downloaded_file if os.path.exists(downloaded_file) else None
    except Exception as e:
        st.error(f"❌ Error downloading: {e}")

if file_path:
    st.write(f"📂 Selected file: {os.path.basename(file_path)}")
    if st.button("🎵 Separate Audio"):
        st.info("⏳ Processing with Demucs...")
        output_folder = os.path.join(SEPARATED_DIR)
        os.makedirs(output_folder, exist_ok=True)
        demucs_command = f"demucs --two-stems=vocals -o {shlex.quote(output_folder)} {shlex.quote(file_path)}"
        process = subprocess.run(demucs_command, shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            st.success("✅ Separation complete! Proceed to recording.")
        else:
            st.error(f"❌ Demucs error: {process.stderr}")

st.header("🎤 Karaoke Recorder")
if file_path:
    song_name = os.path.splitext(os.path.basename(file_path))[0]
    instrumental_path = os.path.join(SEPARATED_DIR, "htdemucs", song_name, "no_vocals.mp3")
    if os.path.exists(instrumental_path):
        duration = get_audio_duration(instrumental_path)
        if duration:
            st.audio(instrumental_path, format='audio/mp3')
            recorded_voice_path = os.path.join(RESULTS_DIR, f"{song_name}_recorded.wav")
            final_karaoke_path = os.path.join(RESULTS_DIR, f"{song_name}_karaoke.wav")
            if st.button("🎧 Start Recording"):
                st.info("🎧 Recording... Speak into the microphone!")
                ffmpeg_format, input_device = get_ffmpeg_audio_device(selected_device_index)
                record_command = f"ffmpeg -f {ffmpeg_format} -i {shlex.quote(input_device)} -t {duration} {shlex.quote(recorded_voice_path)}"
                subprocess.run(record_command, shell=True, check=True)
                if os.path.exists(recorded_voice_path):
                    st.success("✅ Recording complete!")
