"""Parser para chat de Kick."""

import json
import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from parsers.base import ChatParser


class KickParser(ChatParser):
    """Parsea chat de Kick."""

    def __init__(self, source: str):
        """Inicializa el parser.

        Args:
            source: ruta a JSON de chat o URL de Kick
        """
        super().__init__(source)
        self.is_url = source.startswith("http")

    def parse(self) -> Tuple[List[Tuple[float, str]], str]:
        """Parsea chat de Kick.

        Si source es una URL, intenta descargar con yt-dlp.
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
        """Descarga el chat de un video de Kick con yt-dlp.

        LIMITACIÓN: Kick tiene muy limitadas las APIs públicas de chat.
        yt-dlp no puede descargar chat de Kick directamente.

        Returns:
            Ruta al archivo JSON descargado

        Raises:
            RuntimeError: Kick chat no está disponible públicamente
        """
        video_id = self._extract_video_id(self.source)
        if not video_id:
            raise ValueError(f"No se pudo extraer video_id de Kick: {self.source}")

        self.video_id = video_id

        # Kick no proporciona chat públicamente vía yt-dlp
        raise RuntimeError(
            f"❌ Chat de Kick no disponible: Kick no expone chat públicamente.\n"
            f"   Los videos de Kick pueden no tener chat descargable.\n"
            f"   Considera usar un archivo JSON de chat local si lo tienes disponible.\n"
            f"   Video: {self.source}"
        )

    def _extract_video_id(self, url: str) -> str:
        """Extrae el video_id de una URL de Kick."""
        # Kick URLs: https://kick.com/video/xyz123
        match = re.search(r"kick\.com\/video\/([^/?&\n]+)", url)
        if match:
            return match.group(1)
        return None

    def _parse_chat_json(self, chat_file: str) -> Tuple[List[Tuple[float, str]], str]:
        """Parsea el archivo JSON de chat de Kick."""
        with open(chat_file, encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Archivo de chat no es JSON válido: {e}")

        messages = []

        # Intentar diferentes formatos de Kick
        # Formato 1: Array de mensajes directo
        if isinstance(data, list):
            for msg_obj in data:
                if isinstance(msg_obj, dict):
                    timestamp = msg_obj.get("timestamp")
                    text = msg_obj.get("message") or msg_obj.get("text")

                    # Validar tipos y convertir timestamp
                    try:
                        if timestamp is not None and text:
                            if isinstance(text, str):
                                messages.append((float(timestamp), text))
                    except (ValueError, TypeError):
                        continue

        # Formato 2: Objeto con 'messages' o 'chat'
        elif isinstance(data, dict):
            chat_data = data.get("messages") or data.get("chat") or data.get("events")
            if chat_data and isinstance(chat_data, list):
                for msg_obj in chat_data:
                    if isinstance(msg_obj, dict):
                        timestamp = msg_obj.get("timestamp")
                        text = msg_obj.get("message") or msg_obj.get("text")

                        try:
                            if timestamp is not None and text:
                                if isinstance(text, str):
                                    messages.append((float(timestamp), text))
                        except (ValueError, TypeError):
                            continue
        else:
            raise ValueError(f"Formato de chat desconocido: {type(data)}")

        return messages, self.video_id
