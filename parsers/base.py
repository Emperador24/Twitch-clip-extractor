"""Clase base abstracta para parsers de chat."""

from abc import ABC, abstractmethod
from typing import List, Tuple


class ChatParser(ABC):
    """Parser base para datos de chat de diferentes plataformas.

    Un parser convierte datos de chat de cualquier formato a una lista
    de tuplas (timestamp, mensaje) que puede usar clips_chat.py.
    """

    def __init__(self, source: str):
        """Inicializa el parser.

        Args:
            source: ruta a archivo o identificador (depende del parser)
        """
        self.source = source
        self.messages = []
        self.video_id = None

    @abstractmethod
    def parse(self) -> Tuple[List[Tuple[float, str]], str]:
        """Parsea el chat y retorna mensajes e ID del video.

        Returns:
            Tupla de (lista de (timestamp, mensaje), video_id)
            Timestamps en segundos (float), video_id puede ser None
        """
        pass

    def get_messages(self) -> List[Tuple[float, str]]:
        """Retorna los mensajes parseados."""
        if not self.messages:
            self.messages, self.video_id = self.parse()
        return self.messages

    def get_video_id(self) -> str:
        """Retorna el ID del video parseado."""
        if not self.messages:
            self.messages, self.video_id = self.parse()
        return self.video_id
