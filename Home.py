import streamlit as st
import os
import subprocess
import shlex
import yt_dlp

# Define directories
UPLOAD_DIR = "uploads"
DOWNLOADS_DIR = "downloads"
SEPARATED_DIR = "separated"

for directory in [UPLOAD_DIR, DOWNLOADS_DIR, SEPARATED_DIR]:
    os.makedirs(directory, exist_ok=True)

st.set_page_config(page_title="AI Audio Separator", page_icon="🎵", layout="wide")
st.title("🎶 AI Audio Separator")
st.write("Extract vocals and instrumentals from any song!")

# Initialize session state to track processing status
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Function to download MP3 from YouTube (URL or Song Name)
def download_audio(search_input):
    """Downloads audio using yt-dlp, supporting both YouTube URLs and song name searches."""
    output_path = os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{search_input}" if "youtube.com" not in search_input else search_input, download=True)
            if "entries" in info_dict:
                downloaded_file = ydl.prepare_filename(info_dict["entries"][0]).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            else:
                downloaded_file = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")

            return downloaded_file if os.path.exists(downloaded_file) else None
    except Exception as e:
        st.error(f"❌ Error downloading: {e}")
        return None

# User input for YouTube URL or Song Name
search_input = st.text_input("🎶 Enter YouTube URL or Song Name")
file_path = None

if search_input and st.button("⬇️ Fetch & Download"):
    with st.spinner("⏳ Downloading audio... Please wait..."):
        downloaded_file = download_audio(search_input)

    if downloaded_file and os.path.exists(downloaded_file):
        st.success("✅ Download complete!")
        with open(downloaded_file, "rb") as f:
            st.download_button("🎵 Download MP3", f, file_name=os.path.basename(downloaded_file))
        file_path = downloaded_file
    else:
        st.error("❌ Failed to download audio.")

# ---- File Upload Feature ----
uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])
if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File uploaded: {uploaded_file.name}")

# ---- Audio Separation ----
if file_path and os.path.exists(file_path):
    st.write(f"📂 Selected file: {os.path.basename(file_path)}")

    stem_options = {
        "2 stems (Vocals + Instrumental)": "--two-stems vocals",
        "4 stems (Vocals, Drums, Bass, Other)": ""
    }
    stem_choice = st.selectbox("🎼 Choose how many stems to extract:", list(stem_options.keys()))

    if st.button("🎵 Separate Audio"):
        st.session_state.is_processing = True  # Mark process as running
        st.experimental_rerun()  # Force UI update

    if st.session_state.is_processing:
        with st.spinner("⏳ Processing with Demucs... This may take a while."):
            output_folder = os.path.join(SEPARATED_DIR)
            os.makedirs(output_folder, exist_ok=True)

            demucs_command = f"demucs {stem_options[stem_choice]} -o {shlex.quote(output_folder)} {shlex.quote(file_path)}"
            process = subprocess.run(demucs_command, shell=True, text=True, capture_output=True)

            st.session_state.is_processing = False  # Mark process as finished
            st.experimental_rerun()  # Force UI update

    # Display results only after separation is complete
    if not st.session_state.is_processing:
        song_name = os.path.splitext(os.path.basename(file_path))[0]
        stem_folder = os.path.join(SEPARATED_DIR, "htdemucs", song_name)

        if os.path.exists(stem_folder):
            st.success("✅ Separation complete!")
            for stem in os.listdir(stem_folder):
                stem_path = os.path.join(stem_folder, stem)
                st.audio(stem_path)
                with open(stem_path, "rb") as f:
                    st.download_button(f"Download {stem}", f, file_name=stem)
        else:
            st.error("❌ Separation failed: Output folder not found.")