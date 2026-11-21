"""Parsers de chat para diferentes plataformas."""

from parsers.base import ChatParser
from parsers.twitch import TwitchParser
from parsers.youtube import YouTubeParser
from parsers.kick import KickParser

__all__ = ["ChatParser", "TwitchParser", "YouTubeParser", "KickParser"]


def get_parser(platform: str, source: str) -> ChatParser:
    """Factory para obtener el parser correcto basado en la plataforma.

    Args:
        platform: 'twitch', 'youtube' o 'kick'
        source: ruta del archivo JSON o URL

    Returns:
        Instancia del parser correcto
    """
    parsers = {
        "twitch": TwitchParser,
        "youtube": YouTubeParser,
        "kick": KickParser,
    }

    if platform not in parsers:
        raise ValueError(f"Plataforma desconocida: {platform}")

    return parsers[platform](source)
