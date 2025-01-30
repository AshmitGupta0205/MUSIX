import os
import streamlit as st
import sounddevice as sd
import numpy as np
import soundfile as sf
import subprocess
import threading
import time

# Define paths
MUSIX_DIR = "MUSIX"
RECORDINGS_DIR = os.path.join(MUSIX_DIR, "recordings")
OUTPUT_DIR = os.path.join(MUSIX_DIR, "outputs")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# File paths
NON_VOCALS_PATH = None  # Will be set after file upload
RECORDED_VOICE_PATH = os.path.join(RECORDINGS_DIR, "recorded_voice.wav")
CLEANED_VOICE_PATH = os.path.join(RECORDINGS_DIR, "cleaned_voice.wav")
FINAL_TRACK_PATH = os.path.join(RECORDINGS_DIR, "final_karaoke_mix.wav")

# Streamlit UI
st.title("🎤 Karaoke Recorder")
st.write("Upload your `non_vocals.wav` track, record your voice, and create a karaoke mix.")

# Upload non_vocals.wav
uploaded_file = st.file_uploader("📂 Upload `non_vocals.wav`", type=["wav"])

if uploaded_file:
    NON_VOCALS_PATH = os.path.join(RECORDINGS_DIR, "non_vocals.wav")
    with open(NON_VOCALS_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {NON_VOCALS_PATH}")

# Check if non_vocals.wav exists
if not NON_VOCALS_PATH or not os.path.exists(NON_VOCALS_PATH):
    st.warning("⚠ Please upload `non_vocals.wav` before proceeding.")
    st.stop()

# Select Input (Mic) and Output Devices
device_list = sd.query_devices()
st.write("🔍 Available Audio Devices:")
st.write(device_list)

input_device = st.number_input("🎙 Select Input Device (Mic)", min_value=0, value=2)
output_device = st.number_input("🔊 Select Output Device (Speakers)", min_value=0, value=3)

samplerate = 44100
channels = 1  # Microphones are usually mono

# Function to record audio
def record_audio():
    global recording
    recording = True
    recorded_audio = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            recorded_audio.append(indata.copy())

    with sd.InputStream(callback=callback, device=input_device, samplerate=samplerate, channels=channels):
        print("🎤 Recording started... Press stop button to finish.")
        while recording:
            time.sleep(0.1)

    sf.write(RECORDED_VOICE_PATH, np.concatenate(recorded_audio), samplerate)
    print(f"✅ Recording saved: {RECORDED_VOICE_PATH}")

# Button to start recording
if st.button("🎙 Start Recording"):
    threading.Thread(target=record_audio, daemon=True).start()
    st.success("Recording started! 🎤🎶")

# Button to stop recording
if st.button("⏹ Stop Recording"):
    recording = False
    st.success(f"✅ Recording saved: {RECORDED_VOICE_PATH}")

# Noise Removal using Demucs (Fix: Apply to recorded_voice.wav, NOT non_vocals.wav)
if os.path.exists(RECORDED_VOICE_PATH):
    if st.button("🧼 Remove Background Noise"):
        demucs_command = f"demucs --two-stems accompaniment -o {RECORDINGS_DIR} {RECORDED_VOICE_PATH}"
        subprocess.run(demucs_command, shell=True)
        cleaned_path = os.path.join(RECORDINGS_DIR, "htdemucs", "recorded_voice", "no_vocals.wav")

        if os.path.exists(cleaned_path):
            os.rename(cleaned_path, CLEANED_VOICE_PATH)
            st.success(f"✅ Background noise removed! Cleaned vocals saved as: {CLEANED_VOICE_PATH}")
        else:
            st.error("❌ Failed to clean vocals.")

# Merge cleaned vocals with non_vocals.wav
if os.path.exists(CLEANED_VOICE_PATH):
    if st.button("🎶 Merge Karaoke Track"):
        karaoke_data, sr = sf.read(NON_VOCALS_PATH)
        vocals_data, sr = sf.read(CLEANED_VOICE_PATH)

        # Ensure both tracks have the same length
        min_length = min(len(karaoke_data), len(vocals_data))
        merged_audio = karaoke_data[:min_length] + vocals_data[:min_length]

        # Save merged audio
        sf.write(FINAL_TRACK_PATH, merged_audio, samplerate)
        st.success(f"✅ Karaoke Mix Created: {FINAL_TRACK_PATH}")

        # Provide download link
        with open(FINAL_TRACK_PATH, "rb") as f:
            st.download_button("📥 Download Karaoke Mix", f, file_name="final_karaoke_mix.wav")
