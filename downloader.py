import threading
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
import yt_dlp
import time


class DownloadWorker(QObject):
    progress_signal = pyqtSignal(float, str, str)
    finished_signal = pyqtSignal(str, str, str)
    error_signal = pyqtSignal(str)

    def __init__(self, url: str, download_path: str, format_code: str, postprocessor: Optional[str] = None):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.format_code = format_code
        self.postprocessor = postprocessor
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._cancelled = False

    def run(self):
        ydl_opts = {
            'format': self.format_code,
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        if self.postprocessor == "mp3":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                title = info_dict.get('title', 'Unknown Title')
                ext = info_dict.get('ext', 'mp4')
                filepath = f"{self.download_path}/{title}.{ext}"
                self.finished_signal.emit(title, filepath, self.url)
        except Exception as e:
            self.error_signal.emit(str(e))

    def _progress_hook(self, d):
        while not self._pause_event.is_set():
            time.sleep(0.1)
            if self._cancelled:
                raise yt_dlp.utils.DownloadError("Download cancelled by user.")
        if d['status'] == 'downloading':
            try:
                progress = float(d.get('_percent_str', '0.0%').replace('%', '').strip())
            except Exception:
                progress = 0.0
            speed = d.get('_speed_str', '')
            eta = d.get('_eta_str', '')
            self.progress_signal.emit(progress, speed, eta)

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def cancel(self):
        self._cancelled = True
        self._pause_event.set()


class DownloadManager(QObject):
    progress_updated = pyqtSignal(float, str, str)
    download_finished = pyqtSignal(str, str, str)
    download_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.worker = None

    def start_download(self, url: str, download_path: str, format_code: str, postprocessor: Optional[str] = None):
        if self.worker_thread and self.worker_thread.is_alive():
            self.download_error.emit("Another download is already in progress.")
            return
        self.worker = DownloadWorker(url, str(download_path), format_code, postprocessor)
        self.worker.progress_signal.connect(self.progress_updated)
        self.worker.finished_signal.connect(self.download_finished)
        self.worker.error_signal.connect(self.download_error)
        self.worker_thread = threading.Thread(target=self.worker.run, daemon=True)
        self.worker_thread.start()

    def pause_download(self):
        if self.worker:
            self.worker.pause()

    def resume_download(self):
        if self.worker:
            self.worker.resume()

    def cancel_download(self):
        if self.worker:
            self.worker.cancel()
