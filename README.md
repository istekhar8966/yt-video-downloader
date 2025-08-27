# Modern yt-dlp Downloader

## Project Overview
A modern and user-friendly GUI-based video/audio downloader using yt-dlp and PyQt6.  
This downloader supports downloading videos and audios from YouTube and many other supported websites.  
Features include format selection, custom download folder, real-time progress with pause/resume/cancel controls, download history, and dark/light mode toggle.

## Setup Instructions

1. **System Requirements:**  
   - Python 3.10 or higher  
   - FFmpeg installed and added to your system PATH (required for audio conversion)

2. **Installing Dependencies:**  
   Open your terminal or command prompt and run the following command:  
   ```yaml
   pip install -r requirements.txt
   ```
   ## *If you face any issues installing the dependencies, try creating and activating a virtual environment before installing:
   ```python -m venv .venv```

On Linux/macOS:
```source .venv/bin/activate```

On Windows:
   ```yaml
.venv\Scripts\activate
pip install -r requirements.txt
```

text

3. **Running the Application:**  
```python gui.py```

text

## Features
- Download videos and audio from YouTube and other supported sites  
- Choose output formats like MP4, MP3, MKV, 720p, 1080p  
- Select or change the download folder before downloading  
- View download progress with speed and ETA  
- Pause, Resume, and Cancel downloads  
- Download history with clickable entries to open files  
- Dark Mode and Light Mode toggle  
- Sidebar navigation with Home, History, and Settings tabs  

## Notes
- FFmpeg is mandatory for audio extraction and conversion tasks.  
- This project is cross-platform and should work on Windows, Linux, and macOS.  
- For any issues or feature requests, feel free to open an issue on the project repository.

---

Thank you for using the Modern yt-dlp Downloader!

