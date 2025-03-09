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

search_input = st.text_input("🎶 Enter YouTube URL or Song Name")
file_path = None

if search_input and st.button("⬇️ Fetch & Download"):
    st.info("⏳ Searching and downloading audio from YouTube...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{search_input}", download=True)
            downloaded_file = ydl.prepare_filename(info_dict["entries"][0]).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            file_path = downloaded_file if os.path.exists(downloaded_file) else None
    except Exception as e:
        st.error(f"❌ Error downloading: {e}")

uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])
if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File uploaded: {uploaded_file.name}")

if file_path and os.path.exists(file_path):
    st.write(f"📂 Selected file: {os.path.basename(file_path)}")
    if st.button("🎵 Separate Audio"):
        st.info("⏳ Processing with Demucs... This may take a while.")
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
    instrumental_path = None
    instrumental_folder = os.path.join(SEPARATED_DIR, "htdemucs", song_name)

    if os.path.exists(instrumental_folder):
        for file in os.listdir(instrumental_folder):
            if "no_vocals" in file or "instrumental" in file:
                instrumental_path = os.path.join(instrumental_folder, file)
                break

    if instrumental_path and os.path.exists(instrumental_path):
        duration = get_audio_duration(instrumental_path)
        if duration:
            st.audio(instrumental_path, format='audio/mp3')
            recorded_voice_path = os.path.join(RESULTS_DIR, f"{song_name}_recorded.wav")
            final_karaoke_path = os.path.join(RESULTS_DIR, f"{song_name}_karaoke.wav")

            if st.button("🎧 Start Recording"):
                recording_status = st.empty()  # Placeholder for updating status
                recording_status.info("🎧 Recording... Speak into the microphone!")
                
                system_os = platform.system()
                
                if system_os == "Windows":
                    record_command = f'ffmpeg -f dshow -i audio="default" -t {duration} {shlex.quote(recorded_voice_path)}'
                elif system_os == "Darwin":  # macOS
                    record_command = f"ffmpeg -f avfoundation -i :0 -t {duration} {shlex.quote(recorded_voice_path)}"
                else:  # Linux
                    record_command = f"ffmpeg -f alsa -i default -t {duration} {shlex.quote(recorded_voice_path)}"

                process = subprocess.Popen(record_command, shell=True)
                process.wait()  # Wait for recording to finish

                recording_status.empty()  # Clears the "Recording..." message
                st.success("✅ Recording complete!")

                if os.path.exists(recorded_voice_path):
                    st.success("✅ Recording complete!")

                    merge_command = (
                        f"ffmpeg -i {shlex.quote(instrumental_path)} -i {shlex.quote(recorded_voice_path)} "
                        "-filter_complex '[0:a]volume=0.7[a0];[1:a]volume=1.5[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=2' "
                        f"{shlex.quote(final_karaoke_path)}"
                    )
                    subprocess.run(merge_command, shell=True, check=True)

                    if os.path.exists(final_karaoke_path):
                        st.success("✅ Karaoke track created!")
                        st.audio(final_karaoke_path, format='audio/wav')
                        with open(final_karaoke_path, "rb") as f:
                            st.download_button("⬇️ Download Karaoke Track", f, file_name=os.path.basename(final_karaoke_path))
                    else:
                        st.error("❌ Merging failed!")
                else:
                    st.error("❌ Recording failed! Check your microphone settings.")
    else:
        st.warning("⚠️ No instrumental track found. Please separate audio first!")