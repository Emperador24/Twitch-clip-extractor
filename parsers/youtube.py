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
        # Extraer video_id de la URL
        video_id = self._extract_video_id(self.source)
        if not video_id:
            raise ValueError(f"No se pudo extraer video_id de: {self.source}")

        self.video_id = video_id

        # Crear nombre de archivo temporal
        base_name = f"youtube_{video_id}"

        # Descargar chat con yt-dlp
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--sub-lang", "live_chat",
            "--skip-download",
            "-o", base_name,
            self.source,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error descargando chat de YouTube: {e.stderr.decode()}")

        # Buscar archivo .live_chat.json generado
        chat_file = Path(f"{base_name}.en.live_chat.json")
        if not chat_file.exists():
            raise FileNotFoundError(f"No se generó chat JSON: {chat_file}")

        return str(chat_file)

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

        El formato de yt-dlp para live_chat es complejo, extraemos timestamps y mensajes.
        """
        with open(chat_file, encoding="utf-8") as f:
            data = json.load(f)

        messages = []

        # Formato de yt-dlp: array de eventos, cada uno con 'replayChatItemAction'
        for event in data.get("events", []):
            if "replayChatItemAction" in event:
                item = event["replayChatItemAction"].get("actions", [{}])[0]

                # Buscar mensaje de chat
                if "addChatItemAction" in item:
                    chat_item = item["addChatItemAction"].get("item", {})
                    msg_data = chat_item.get("liveChatMessageRenderer", {})

                    timestamp_text = msg_data.get("timestampText", {}).get("simpleText", "")
                    message_text = ""

                    # Extraer texto del mensaje
                    runs = msg_data.get("message", {}).get("runs", [])
                    for run in runs:
                        message_text += run.get("text", "")

                    # Convertir timestamp "HH:MM:SS" a segundos
                    if timestamp_text and message_text:
                        seconds = self._parse_timestamp(timestamp_text)
                        if seconds is not None:
                            messages.append((float(seconds), message_text))

        # Si no encontramos mensajes con esta estructura, intentar formato alternativo
        if not messages:
            messages = self._parse_chat_legacy(data)

        video_id = self.video_id or self._extract_video_id_from_chat(data)

        return messages, video_id

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
        except (ValueError, AttributeError):
            pass
        return None

    def _parse_chat_legacy(self, data: dict) -> List[Tuple[float, str]]:
        """Fallback para parsear formato alternativo de chat."""
        messages = []
        for item in data.get("items", []):
            if "id" in item and "message" in item:
                # Formato simple
                msg = item.get("message", "")
                if msg:
                    messages.append((0.0, msg))
        return messages

    def _extract_video_id_from_chat(self, data: dict) -> str:
        """Intenta extraer video_id de los datos del chat."""
        # Algunos formatos pueden incluir metadata del video
        if "videoDetails" in data:
            return data["videoDetails"].get("videoId")
        return None
