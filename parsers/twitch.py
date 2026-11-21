"""Parser para chat de Twitch (formato TwitchDownloader)."""

import json
from typing import List, Tuple
from parsers.base import ChatParser


class TwitchParser(ChatParser):
    """Parsea JSON de chat descargado con TwitchDownloaderCLI."""

    def parse(self) -> Tuple[List[Tuple[float, str]], str]:
        """Parsea archivo JSON de TwitchDownloader.

        El formato esperado es el JSON generado por:
            TwitchDownloaderCLI chatdownload --id <id> -o chat.json

        Returns:
            Tupla de (lista de (timestamp, mensaje), video_id)
        """
        with open(self.source, encoding="utf-8") as f:
            datos = json.load(f)

        messages = []
        for comment in datos.get("comments", []):
            timestamp = comment.get("content_offset_seconds")
            text = (comment.get("message") or {}).get("body", "")
            if timestamp is not None:
                messages.append((float(timestamp), text))

        video_id = (datos.get("video") or {}).get("id")
        return messages, video_id
