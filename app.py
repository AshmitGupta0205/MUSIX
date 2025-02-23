import streamlit as st
import os
import subprocess
import shlex
import yt_dlp
import librosa

# Define directories
UPLOAD_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SEPARATED_DIR = "separated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(SEPARATED_DIR, exist_ok=True)

# ---- UI Setup ----
st.set_page_config(page_title="🎵 AI Audio Separator", page_icon="🎼", layout="wide")
st.title("🎵 AI Audio Separator")
st.write("Extract vocals and instrumentals from any song!")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["🎵 Audio Separator (Home)", "🎤 Karaoke Maker"])

if page == "🎤 Karaoke Maker":
    subprocess.Popen(["streamlit", "run", "karaoke.py"])
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

# Upload Feature
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
    stem_options = {
        "2 stems (Vocals + Instrumental)": "--two-stems vocals",
        "4 stems (Vocals, Drums, Bass, Other)": ""
    }
    stem_choice = st.selectbox("🎼 Choose how many stems to extract:", list(stem_options.keys()))
    
    # 🎵 **"Separate Audio" Button Added Here**
    if st.button("🎵 Separate Audio"):
        st.info("⏳ Processing... This may take a while.")
        output_folder = os.path.join(SEPARATED_DIR)
        os.makedirs(output_folder, exist_ok=True)
        
        demucs_command = f"demucs {stem_options[stem_choice]} -o {output_folder} {shlex.quote(file_path)}"
        process = subprocess.run(demucs_command, shell=True, text=True, capture_output=True)
        
        if process.returncode == 0:
            song_name = os.path.splitext(os.path.basename(file_path))[0]
            stem_folder = os.path.join(output_folder, "htdemucs", song_name)
            
            if os.path.exists(stem_folder):
                for stem in os.listdir(stem_folder):
                    stem_path = os.path.join(stem_folder, stem)
                    st.audio(stem_path)
                    with open(stem_path, "rb") as f:
                        st.download_button(f"Download {stem}", f, file_name=stem)
                st.success("✅ Separation complete!")
            else:
                st.error("❌ Separation failed: Output folder not found.")
        else:
            st.error("❌ Demucs error! Check logs for details.")

st.markdown("---")
if st.button("🎤 Go to Karaoke Maker"):
    subprocess.Popen(["streamlit", "run", "karaoke.py"])
    st.stop()