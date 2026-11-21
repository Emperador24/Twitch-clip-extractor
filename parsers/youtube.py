"""Parser para chat de YouTube (live chat replay)."""

import json
import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from parsers.base import ChatParser


class YouTubeParser(ChatParser):
    """Parsea chat de YouTube descargado con yt-dlp."""

    def __init__(self, source: str):
        """Inicializa el parser.

        Args:
            source: ruta a JSON de chat o URL de YouTube
        """
        super().__init__(source)
        self.is_url = source.startswith("http")

    def parse(self) -> Tuple[List[Tuple[float, str]], str]:
        """Parsea chat de YouTube.

        Si source es una URL, intenta descargar el chat con yt-dlp.
        Si es un archivo local, lo parsea directamente.

        Returns:
            Tupla de (lista de (timestamp, mensaje), video_id)
        """
        if self.is_url:
            chat_file = self._download_chat()
        else:
            chat_file = self.source

        return self._parse_chat_json(chat_file)

    def _download_chat(self) -> str:
        """Descarga el chat de un video de YouTube con yt-dlp.

        Returns:
            Ruta al archivo JSON descargado
        """
        import tempfile

        # Extraer video_id de la URL
        video_id = self._extract_video_id(self.source)
        if not video_id:
            raise ValueError(f"No se pudo extraer video_id de: {self.source}")

        self.video_id = video_id

        # Descargar en tempdir para no contaminar el repo
        tmpdir = tempfile.gettempdir()
        base_name = str(Path(tmpdir) / f"youtube_{video_id}")

        # Descargar chat con yt-dlp (flag correcto: --sub-langs)
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--sub-langs", "live_chat",
            "--skip-download",
            "--ignore-config",
            "-o", base_name,
            "--",
            self.source,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            raise RuntimeError("Timeout descargando chat de YouTube (>300s)")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error descargando chat de YouTube: {e.stderr.decode()}")

        # Buscar archivo .live_chat.json generado (puede tener diferentes prefijos)
        json_files = list(Path(tmpdir).glob(f"{Path(base_name).name}*.live_chat.json"))
        if not json_files:
            raise FileNotFoundError(f"No se generó chat JSON para: {video_id}")

        return str(json_files[0])

    def _extract_video_id(self, url: str) -> str:
        """Extrae el video_id de una URL de YouTube."""
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)",
            r"youtube\.com\/embed\/([^?&\n]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _parse_chat_json(self, chat_file: str) -> Tuple[List[Tuple[float, str]], str]:
        """Parsea el archivo JSON de chat.

        yt-dlp escribe JSON Lines (una línea por objeto JSON).
        Cada línea puede ser un evento con replayChatItemAction.
        """
        messages = []

        try:
            with open(chat_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Formato de yt-dlp: replayChatItemAction contiene actions
                    if "replayChatItemAction" in event:
                        actions = event["replayChatItemAction"].get("actions", [])
                        for action in actions:
                            msg = self._extract_message_from_action(action)
                            if msg:
                                timestamp, text = msg
                                if timestamp is not None and text:
                                    messages.append((float(timestamp), text))

        except (IOError, json.JSONDecodeError) as e:
            raise ValueError(f"Error leyendo archivo de chat: {e}")

        video_id = self.video_id

        return messages, video_id

    def _extract_message_from_action(self, action: dict) -> Tuple[int, str]:
        """Extrae timestamp y texto de un action."""
        if "addChatItemAction" not in action:
            return None

        chat_item = action["addChatItemAction"].get("item", {})
        msg_data = chat_item.get("liveChatMessageRenderer", {})

        if not msg_data:
            return None

        timestamp_text = msg_data.get("timestampText", {}).get("simpleText", "")
        message_text = ""

        # Extraer texto del mensaje
        runs = msg_data.get("message", {}).get("runs", [])
        for run in runs:
            if isinstance(run, dict):
                message_text += run.get("text", "")

        # Convertir timestamp "HH:MM:SS" a segundos
        if timestamp_text and message_text:
            seconds = self._parse_timestamp(timestamp_text)
            if seconds is not None:
                return (seconds, message_text)

        return None

    def _parse_timestamp(self, timestamp_str: str) -> int:
        """Convierte timestamp "HH:MM:SS" o "MM:SS" a segundos."""
        try:
            parts = timestamp_str.split(":")
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = map(int, parts)
                return m * 60 + s
        except (ValueError, AttributeError, TypeError):
            pass
        return None
