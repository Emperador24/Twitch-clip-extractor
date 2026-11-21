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

        Nota: Kick tiene limitaciones con chat público. Este método
        intenta descargar subtitle/chat info disponible.

        Returns:
            Ruta al archivo JSON descargado
        """
        # Extraer video_id de la URL o usar un hash
        video_id = self._extract_video_id(self.source)
        if not video_id:
            # Si no se puede extraer, usar un hash de la URL
            import hashlib
            video_id = hashlib.md5(self.source.encode()).hexdigest()[:16]

        self.video_id = video_id

        # Crear nombre de archivo temporal
        base_name = f"kick_{video_id}"

        # Intentar descargar con yt-dlp
        # Nota: Kick no siempre tiene chat público disponible
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--skip-download",
            "-o", base_name,
            self.source,
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # Si falla, puede ser que el chat no esté disponible
            raise RuntimeError(
                f"Error descargando info de Kick: {e.stderr.decode()}\n"
                "Nota: Algunos videos de Kick pueden no tener chat público disponible."
            )

        # Buscar cualquier archivo JSON generado
        json_files = list(Path(".").glob(f"{base_name}*.json"))
        if json_files:
            return str(json_files[0])

        raise FileNotFoundError(
            f"No se generó chat JSON para Kick: {video_id}.\n"
            "El video puede no tener chat disponible públicamente."
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
            except json.JSONDecodeError:
                # Si no es JSON, intenta parsear como texto plano
                return self._parse_chat_text(chat_file)

        messages = []

        # Intentar diferentes formatos de Kick
        # Formato 1: Array de mensajes directo
        if isinstance(data, list):
            for msg_obj in data:
                if isinstance(msg_obj, dict):
                    timestamp = msg_obj.get("timestamp", 0)
                    text = msg_obj.get("message") or msg_obj.get("text") or ""
                    if text:
                        messages.append((float(timestamp), text))

        # Formato 2: Objeto con 'messages' o 'chat'
        elif isinstance(data, dict):
            chat_data = data.get("messages") or data.get("chat") or data.get("events")
            if chat_data:
                for msg_obj in chat_data if isinstance(chat_data, list) else []:
                    timestamp = msg_obj.get("timestamp", 0)
                    text = msg_obj.get("message") or msg_obj.get("text") or ""
                    if text:
                        messages.append((float(timestamp), text))

        return messages, self.video_id

    def _parse_chat_text(self, chat_file: str) -> Tuple[List[Tuple[float, str]], str]:
        """Fallback para parsear chat en formato texto simple."""
        messages = []
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        # Asumir formato simple: timestamp y mensaje separados
                        messages.append((float(line_num * 10), line))
        except Exception:
            pass
        return messages, self.video_id
