import sqlite3
from pathlib import Path
from datetime import datetime


class HistoryDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path.home() / ".yt_dlp_downloader_history.db")
        self.connection = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    url TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            ''')

    def add_entry(self, title: str, filepath: str, url: str):
        with self.connection:
            self.connection.execute('''
                INSERT INTO downloads (title, filepath, url, date)
                VALUES (?, ?, ?, ?)
            ''', (title, filepath, url, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def get_all_entries(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, title, filepath, url, date FROM downloads ORDER BY date DESC')
        rows = cursor.fetchall()
        return [{"id": r[0], "title": r[1], "filepath": r[2], "url": r[3], "date": r[4]} for r in rows]

    def delete_entry(self, entry_id: int):
        with self.connection:
            self.connection.execute('DELETE FROM downloads WHERE id=?', (entry_id,))

    def close(self):
        if self.connection:
            self.connection.close()
