"""Configuración de plataformas para clips_chat."""

PLATFORMS = {
    "twitch": {
        "minimo": 3.0,
        "antes": 20,
        "despues": 15,
        "reacciones": r"(ja){2,}|j{2,}a|xd+|kekw|lul|omegalul|lmao+|clip|noo+|wtf|pog|😂|🤣|💀",
    },
    "youtube": {
        "minimo": 2.5,
        "antes": 20,
        "despues": 15,
        "reacciones": r"jaja+|ja+ja|xd+|😂|🤣|💀|lol|omg|wow|bruh|🔥|🎉",
    },
    "kick": {
        "minimo": 2.5,
        "antes": 20,
        "despues": 15,
        "reacciones": r"jaja+|ja+ja|xd+|😂|🤣|💀|lol|omg|wow|bruh|clip",
    },
}


def get_platform_config(platform: str, key: str = None, default=None):
    """Obtiene configuración de una plataforma.

    Args:
        platform: 'twitch', 'youtube' o 'kick'
        key: configuración específica (ej 'minimo', 'reacciones')
        default: valor por defecto si no existe

    Returns:
        Diccionario de configuración o valor específico
    """
    if platform not in PLATFORMS:
        raise ValueError(f"Plataforma desconocida: {platform}")

    config = PLATFORMS[platform]
    if key:
        return config.get(key, default)
    return config
