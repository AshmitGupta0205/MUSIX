import streamlit as st
import os
import subprocess
import shlex
import yt_dlp

# Define directories
UPLOAD_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SEPARATED_DIR = "separated"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(SEPARATED_DIR, exist_ok=True)

st.title("🎵 Web-Based AI Audio Separator")
st.write("Upload an MP3 file or fetch from YouTube, then process it using Demucs.")

# Function to check if input is a YouTube URL
def is_youtube_url(input_text):
    return "youtube.com" in input_text or "youtu.be" in input_text

# Function to download from YouTube
def download_youtube_audio(search_query):
    """Download audio from YouTube using yt-dlp. Accepts either a URL or a search term."""
    
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

# **User input for YouTube URL or Song Name**
search_input = st.text_input("🎶 Enter YouTube URL or Song Name")
file_path = None  # Ensure file_path starts as None

# 1️⃣ **Download from YouTube**
if search_input and st.button("⬇️ Fetch & Download"):
    st.info("⏳ Fetching audio from YouTube...")
    downloaded_file_path = download_youtube_audio(search_input)

    if downloaded_file_path and os.path.exists(downloaded_file_path):
        file_path = downloaded_file_path
        st.success(f"✅ Downloaded: {os.path.basename(downloaded_file_path)}")

# 2️⃣ **File Upload Feature**
uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])

if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File uploaded: {uploaded_file.name}")

# **Ensure file_path is assigned properly**
if not file_path and search_input:
    for file in os.listdir(DOWNLOADS_DIR):
        if search_input.lower() in file.lower():
            file_path = os.path.join(DOWNLOADS_DIR, file)
            break

# **Show selected file**
if file_path and os.path.exists(file_path):
    st.write(f"📂 Selected file: `{os.path.basename(file_path)}`")
else:
    st.warning("⚠️ No file selected. Upload or download a song first!")

# 3️⃣ **Show Separation Options If File Exists**
if file_path and os.path.exists(file_path):
    stem_options = {
        "2 stems (Vocals + Instrumental)": "--two-stems vocals",
        "4 stems (Vocals, Drums, Bass, Other)": ""
    }
    stem_choice = st.selectbox("🎛️ Choose how many stems to extract:", list(stem_options.keys()))

    if st.button("🎶 Separate Audio"):
        st.info("⏳ Processing... This may take a while.")

        # Ensure safe file paths
        safe_file_path = shlex.quote(file_path)
        output_folder = os.path.join(SEPARATED_DIR)
        os.makedirs(output_folder, exist_ok=True)

        # **🔍 Debugging Step: Print the command**
        demucs_command = f"demucs {stem_options[stem_choice]} -o {output_folder} {safe_file_path}"
        #st.write(f"🚀 Running command: `{demucs_command}`")

        # Run Demucs and capture output
        process = subprocess.run(demucs_command, shell=True, text=True, capture_output=True)

        st.write("🔍 **Demucs Output:**")
        if process.returncode != 0:
            st.error(f"❌ Demucs error! Check the logs above for details.")
        else:
            song_name = os.path.splitext(os.path.basename(file_path))[0]
            stem_folder = os.path.join(output_folder, "htdemucs", song_name)  # Ensure correct path

            if os.path.exists(stem_folder) and os.listdir(stem_folder):  # Ensure files exist
                st.success("✅ Separation complete! Download your files below:")
                for stem in os.listdir(stem_folder):
                    stem_path = os.path.join(stem_folder, stem)
                    st.audio(stem_path)
                    with open(stem_path, "rb") as f:
                        st.download_button(f"Download {stem}", f, file_name=stem)
            else:
                st.error("❌ Separation failed: Output folder not found or empty.")