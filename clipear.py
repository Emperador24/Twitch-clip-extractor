#!/usr/bin/env python3
"""clipear.py: Pasa un link y genera clips automáticamente.

Uso:
  python3 clipear.py "https://www.twitch.tv/videos/123456789"
  python3 clipear.py "https://www.youtube.com/watch?v=abc123xyz"
  python3 clipear.py "https://kick.com/video/xyz789"

  Opciones:
  --clips N          Cuántos clips (default: 10)
  --minimo N         Sensibilidad (default: según plataforma)
  --sin-cortar       Solo mostrar picos sin descargar videos
"""

import argparse
import os
import re
import subprocess
import sys


def extraer_info_url(url):
    """Extrae la plataforma y video ID de una URL.

    Args:
        url: URL de Twitch, YouTube o Kick

    Returns:
        (plataforma, video_id) o (None, None) si no es válida
    """
    from urllib.parse import urlparse

    url = url.strip()

    # Parsear URL para validar
    try:
        parsed = urlparse(url)
    except Exception:
        return None, None

    # Validar que sea HTTP/HTTPS
    if parsed.scheme not in {"http", "https"}:
        return None, None

    hostname = parsed.hostname or ""

    # Twitch
    if "twitch.tv" in hostname:
        match = re.search(r"twitch\.tv/videos/(\d+)", url)
        if match:
            video_id = match.group(1)
            # Validar que sea solo dígitos (6+)
            if re.fullmatch(r"\d{6,}", video_id):
                return "twitch", video_id
        return None, None

    # YouTube
    if "youtube.com" in hostname or "youtu.be" in hostname:
        # Validar que el video ID sea correcto
        match = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]+)", url)
        if match:
            video_id = match.group(1)
            # YouTube IDs son exactamente 11 caracteres alphanumeric + - _
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
                return "youtube", video_id
        return None, None

    # Kick
    if "kick.com" in hostname:
        # Formato 1: https://kick.com/video/xyz789
        match = re.search(r"kick\.com/video/([A-Za-z0-9_-]+)", url)
        if match:
            return "kick", match.group(1)
        # Formato 2: https://kick.com/username/videos/uuid-style-id
        match = re.search(r"kick\.com/[^/]+/videos/([A-Za-z0-9_-]+)", url)
        if match:
            return "kick", match.group(1)
        return None, None

    return None, None


def descargar_chat_twitch(video_id):
    """Descarga chat de Twitch con TwitchDownloaderCLI."""
    archivo_chat = f"chat_{video_id}.json"

    if os.path.exists(archivo_chat):
        print(f"✅ Chat ya existe: {archivo_chat}")
        return archivo_chat

    print(f"📥 Descargando chat de Twitch {video_id}...")
    # Buscar TwitchDownloaderCLI en la carpeta actual o en PATH
    cli_path = "./TwitchDownloaderCLI"
    if not os.path.exists(cli_path):
        cli_path = "TwitchDownloaderCLI"  # Buscar en PATH

    cmd = [cli_path, "chatdownload", "--id", video_id, "-o", archivo_chat]

    try:
        # Aumentar timeout para chats grandes (hasta 30 minutos)
        subprocess.run(cmd, check=True, capture_output=False, timeout=1800)
        print(f"✅ Chat descargado: {archivo_chat}")
        return archivo_chat
    except FileNotFoundError:
        print("❌ TwitchDownloaderCLI no encontrado")
        print("   Descárgalo desde: https://github.com/lay295/TwitchDownloader/releases")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error descargando chat: {e}")
        return None
    except subprocess.TimeoutExpired:
        print("❌ Timeout descargando chat (el chat es MUY grande, directo muy largo)")
        print("   Intenta con un directo más corto o ejecuta con --sin-cortar")
        return None


def generar_clips(url, plataforma, video_id, opciones):
    """Ejecuta clips_chat.py para generar clips."""
    print(f"\n🎬 Generando clips...")
    print(f"   Plataforma: {plataforma.upper()}")
    print(f"   Video ID: {video_id}")

    if plataforma == "twitch":
        chat_file = f"chat_{video_id}.json"

        if not os.path.exists(chat_file):
            print(f"❌ Chat no encontrado: {chat_file}")
            return False

        cmd = [
            "python3",
            "clips_chat.py",
            chat_file,
            "--vod",
            video_id,
            "--plataforma",
            plataforma,
        ]
    else:
        # Para YouTube y Kick, pasar URL directa
        cmd = [
            "python3",
            "clips_chat.py",
            url,
            "--plataforma",
            plataforma,
        ]

    # Agregar opciones
    if opciones.get("clips"):
        cmd.extend(["--clips", str(opciones["clips"])])
    if opciones.get("minimo"):
        cmd.extend(["--minimo", str(opciones["minimo"])])
    if opciones.get("cortar"):
        cmd.append("--cortar")

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ ¡Clips generados correctamente!")
        print("   📁 Los clips están en: ./clips/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generando clips: {e}")
        return False
    except FileNotFoundError:
        print("❌ clips_chat.py no encontrado en la carpeta actual")
        return False


def main():
    p = argparse.ArgumentParser(
        description="Pasa un link y genera clips automáticamente.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 clipear.py "https://www.twitch.tv/videos/123456789"
  python3 clipear.py "https://www.youtube.com/watch?v=abc123xyz" --clips 5
  python3 clipear.py "https://kick.com/video/xyz789" --minimo 2.0
        """,
    )
    p.add_argument("url", help="Link del directo (Twitch, YouTube o Kick)")
    p.add_argument("--clips", type=int, default=10, help="Cuántos clips (default: 10)")
    p.add_argument(
        "--minimo",
        type=float,
        help="Sensibilidad (default: según plataforma)",
    )
    p.add_argument(
        "--sin-cortar",
        action="store_true",
        help="Solo mostrar picos sin descargar/procesar videos",
    )
    a = p.parse_args()

    # Verificar que clips_chat.py existe
    if not os.path.exists("clips_chat.py"):
        print("❌ clips_chat.py no encontrado en la carpeta actual")
        sys.exit(1)

    # Extraer info de la URL
    plataforma, video_id = extraer_info_url(a.url)

    if not plataforma:
        print("❌ URL no reconocida")
        print("   Formatos válidos:")
        print("   - Twitch:  https://www.twitch.tv/videos/123456789")
        print("   - YouTube: https://www.youtube.com/watch?v=abc123xyz")
        print("   - Kick:    https://kick.com/video/xyz789")
        sys.exit(1)

    print("=" * 60)
    print("🎬 GENERAR CLIPS")
    print("=" * 60)
    print(f"URL: {a.url}")
    print(f"Plataforma: {plataforma.upper()}")
    print(f"Video ID: {video_id}")
    print(f"Clips a generar: {a.clips}")
    if a.minimo:
        print(f"Sensibilidad: {a.minimo}")
    print()

    # Descargar chat si es Twitch
    if plataforma == "twitch":
        chat_file = descargar_chat_twitch(video_id)
        if not chat_file:
            sys.exit(1)

    # Preparar opciones
    opciones = {
        "clips": a.clips,
        "minimo": a.minimo,
        "cortar": not a.sin_cortar,
    }

    # Generar clips
    success = generar_clips(a.url, plataforma, video_id, opciones)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
