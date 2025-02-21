import os
import streamlit as st
import yt_dlp
import sounddevice as sd
import numpy as np
import wave
import shutil

# Folder paths
downloads_folder = "downloads"
separated_folder = "separated"
results_folder = "results"

# Ensure folders exist
os.makedirs(downloads_folder, exist_ok=True)
os.makedirs(separated_folder, exist_ok=True)
os.makedirs(results_folder, exist_ok=True)

st.title("Karaoke Maker 🎤🎶")

# User enters the song name
song_name = st.text_input("Enter song name:")
if song_name:
    song_filename = f"{song_name}.mp3"
    song_path = os.path.join(downloads_folder, song_filename)

    # Check if the song already exists before downloading
    if not os.path.exists(song_path):
        st.write("Downloading song...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            if 'entries' in info:
                song_path = os.path.join(downloads_folder, f"{info['entries'][0]['title']}.mp3")
            else:
                st.error("Failed to download song.")
                st.stop()
    else:
        st.write("Song already downloaded. Skipping download.")

    # Extract instrumental (Demucs processing)
    # Extract instrumental (Demucs processing)
    instrumental_path = os.path.join(separated_folder, f"{song_name}_no_vocals.wav")
    if not os.path.exists(instrumental_path):
        st.write("Extracting instrumental track...")
        os.system(f'demucs --two-stems=vocals -o "{separated_folder}" "{song_path}"')
        
        # Move the extracted instrumental to the correct location
        extracted_folder = os.path.join(separated_folder, song_name)
        extracted_file = os.path.join(extracted_folder, "no_vocals.wav")
        if os.path.exists(extracted_file):
            shutil.move(extracted_file, instrumental_path)
        else:
            st.error("Instrumental file not found! Check extraction process.")
            st.stop()
    else:
        st.write("Instrumental already extracted.")

    # Play instrumental
    st.audio(instrumental_path)

    # Get instrumental duration from the WAV file
    def get_audio_duration(wav_file):
        with wave.open(wav_file, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)

    instrumental_duration = get_audio_duration(instrumental_path)

    # Record user voice
    st.write(f"Recording for {int(instrumental_duration)} seconds. Sing now!")
    duration = int(instrumental_duration)  # Match instrumental duration
    samplerate = 44100  # Standard sample rate

    recorded_audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    # Save recorded voice
    recorded_path = os.path.join(results_folder, "user_voice.wav")
    with wave.open(recorded_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(samplerate)
        wf.writeframes(recorded_audio.tobytes())

    # Merge instrumental and recorded voice
    final_output_path = os.path.join(results_folder, "final_karaoke.wav")

    def merge_audio_tracks(track1, track2, output_file):
        with wave.open(track1, "rb") as wf1, wave.open(track2, "rb") as wf2:
            if wf1.getnframes() > wf2.getnframes():
                padding = wf1.getnframes() - wf2.getnframes()
                recorded_audio = np.pad(np.frombuffer(wf2.readframes(wf2.getnframes()), dtype=np.int16),
                                        (0, padding), 'constant')
            else:
                recorded_audio = np.frombuffer(wf2.readframes(wf2.getnframes()), dtype=np.int16)

            instrumental_audio = np.frombuffer(wf1.readframes(wf1.getnframes()), dtype=np.int16)
            merged_audio = instrumental_audio + recorded_audio

            with wave.open(output_file, "wb") as wf_out:
                wf_out.setnchannels(1)
                wf_out.setsampwidth(2)  # 16-bit audio
                wf_out.setframerate(wf1.getframerate())
                wf_out.writeframes(merged_audio.astype(np.int16).tobytes())

    merge_audio_tracks(instrumental_path, recorded_path, final_output_path)

    # Provide download button
    st.success("Karaoke track is ready!")
    with open(final_output_path, "rb") as f:
        st.download_button("Download Karaoke Track", f, file_name="karaoke_output.wav", mime="audio/wav")