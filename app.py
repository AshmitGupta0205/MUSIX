import streamlit as st
import os
import subprocess
import shlex  # For safely escaping paths

# Define directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.title("🎵 Web-Based AI Audio Separator")
st.write("Upload an MP3 file, select the number of stems, and process the file using Demucs.")

# File Upload
uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav"])

if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Display success message immediately after upload
    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # User selection for stems (moved below success message)
    stem_options = {
        "2 stems (Vocals + Instrumental)": "--two-stems vocals",
        "4 stems (Vocals, Drums, Bass, Other)": ""
    }
    stem_choice = st.selectbox("🎛️ Choose how many stems to extract:", list(stem_options.keys()))

    # Run Demucs when button is clicked
    if st.button("🎶 Separate Audio"):
        st.info("⏳ Processing... This may take a while.")

        # Safely escape the file paths using shlex.quote
        safe_file_path = shlex.quote(file_path)
        safe_output_dir = shlex.quote(OUTPUT_DIR)

        # Get selected stem option
        demucs_command = f"demucs {stem_options[stem_choice]} -o {safe_output_dir} {safe_file_path}"
        
        # Run the Demucs command
        subprocess.run(demucs_command, shell=True)

        # Find extracted stems
        stem_folder = os.path.join(OUTPUT_DIR, "htdemucs", uploaded_file.name[:-4])

        if os.path.exists(stem_folder):
            st.success("✅ Separation complete! Download your files below:")

            for stem in os.listdir(stem_folder):
                stem_path = os.path.join(stem_folder, stem)
                
                st.audio(stem_path)  # Play extracted audio
                with open(stem_path, "rb") as f:
                    st.download_button(f"Download {stem}", f, file_name=stem)