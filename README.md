# MUSIX - AI-Powered Audio Processing

MUSIX is a web-based application that provides advanced audio processing capabilities using AI models like **htdemucs**. The project consists of two main components:

1. **app.py - Web-Based AI Audio Separator**
2. **karaoke.py - Karaoke Maker**

---

## 🎵 Web-Based AI Audio Separator (`app.py`)
This tool allows users to separate vocals and instrumentals from songs using the **htdemucs** model.

### Features:
- **Upload an MP3/WAV file** or fetch a song from **YouTube**.
- **Separate audio into different stems** (Vocals, Instrumental, Drums, Bass, Other).
- **Download processed stems** after separation.
- **Uses htdemucs** for high-quality music separation.

### How to Use:
1. Run `app.py` using Streamlit:
   ```bash
   streamlit run app.py
   ```
2. Upload an audio file or enter a YouTube link.
3. Select the number of stems to extract.
4. Click "Separate Audio" and download the results.

---

## 🎤 Karaoke Maker (`karaoke.py`)
This module transforms a song into a **karaoke track** by removing vocals and allowing users to sing along.

### Features:
- **Fetch songs from an online API** and download the track.
- **Remove vocals** using htdemucs to keep only the instrumental.
- **Play the instrumental track** while recording the user's voice.
- **Merge the recorded voice with the instrumental** to create a final karaoke mix.
- **Includes pitch shifting** and **lyrics display** for a better experience.

### How to Use:
1. Run `karaoke.py` separately:
   ```bash
   streamlit run karaoke.py
   ```
2. Enter a song name to fetch and process it.
3. Sing along while the instrumental plays in the background.
4. Save and download the final karaoke mix.

---

## 📂 Project Directory Structure
```
MUSIX/
│── app.py          # Web-based AI Audio Separator
│── karaoke.py      # Karaoke Maker
│── downloads/      # Stores downloaded songs
│── uploads/        # Stores uploaded audio files
│── separated/      # Stores extracted stems
│── results/        # Stores processed audio results
│── README.md       # Project documentation
```

---

## 🚀 Installation & Setup
To set up the project, install dependencies:
```bash
pip install -r requirements.txt
```

Ensure you have **htdemucs**, **yt-dlp**, **Streamlit**, and **FFmpeg** installed.

---

## 📌 Notes
- `app.py` runs on **Streamlit** for an easy-to-use web interface.
- `karaoke.py` is a separate module that focuses on karaoke functionality.
- Output files are stored in the `separated/` and `outputs/` folders.

---

## 🌟 Contributing
Feel free to contribute to **MUSIX** by submitting issues or pull requests!

---

## 📜 License
This project is open-source and available under the MIT License.

