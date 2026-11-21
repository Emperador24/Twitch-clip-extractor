#!/usr/bin/env python3
"""clips_chat.py: encuentra los mejores momentos de directos mirando el chat
y los corta en vídeo vertical para Reels, TikTok y Shorts.

Soporta: Twitch, YouTube y Kick.

La idea: cuando pasa algo en directo, el chat explota. Ese pico es tu clip.
El chat reacciona tarde, así que el clip empieza 20 segundos antes del pico.

Necesitas:
  - Python 3.9 o más nuevo.
  - El chat del directo en JSON (descargado con TwitchDownloaderCLI para Twitch,
    o automáticamente para YouTube/Kick).
  - Para cortar el vídeo: yt-dlp y ffmpeg instalados.

Uso:
  # Twitch (compatible con versión anterior)
  python3 clips_chat.py chat.json --vod 123456 --cortar

  # YouTube (automático o con chat local)
  python3 clips_chat.py https://www.youtube.com/watch?v=abc123 --cortar
  python3 clips_chat.py chat.json --plataforma youtube --video-id abc123 --cortar

  # Kick
  python3 clips_chat.py https://kick.com/video/abc123 --cortar

Úsalo solo con creadores que permiten que se recorten sus directos.
"""
import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

from parsers import get_parser
from config import get_platform_config


def detectar_plataforma(fuente: str) -> str:
    """Detecta la plataforma basada en la URL o fuente."""
    fuente_lower = fuente.lower()
    if "youtube.com" in fuente_lower or "youtu.be" in fuente_lower:
        return "youtube"
    elif "kick.com" in fuente_lower:
        return "kick"
    elif "twitch.tv" in fuente_lower:
        return "twitch"
    # Por defecto, asumir que es Twitch si es un archivo local
    elif fuente.endswith(".json"):
        return "twitch"
    return "twitch"


def leer_chat(fuente: str, plataforma: str = None, video_id: str = None):
    """Lee y parsea el chat según la plataforma.

    Args:
        fuente: ruta a archivo JSON o URL del video
        plataforma: 'twitch', 'youtube' o 'kick' (detectado automáticamente si no se proporciona)
        video_id: ID del video (opcional, para cuando fuente es archivo local)

    Returns:
        Tupla de (mensajes, video_id, plataforma)

    Raises:
        ValueError: Si hay error parseando el chat
        FileNotFoundError: Si el archivo no existe
    """
    if not plataforma:
        plataforma = detectar_plataforma(fuente)

    try:
        parser = get_parser(plataforma, fuente)
        mensajes, vod = parser.parse()

        # Si se proporciona video_id explícitamente, usarlo
        if video_id:
            vod = video_id

        return mensajes, vod, plataforma
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Error parseando chat: {e}") from e
    except Exception as e:
        raise ValueError(f"Error inesperado parseando chat: {e}") from e


def contar(mensajes, ventana, reacciones_pattern=None):
    """Puntos de cada tramo de `ventana` segundos: 1 por mensaje, 2 si es una reacción."""
    if not mensajes:
        return []

    if reacciones_pattern is None:
        reacciones_pattern = re.compile(
            r"(ja){2,}|j{2,}a|xd+|kekw|lul|omegalul|lmao+|clip|noo+|wtf|pog|😂|🤣|💀",
            re.IGNORECASE,
        )
    else:
        reacciones_pattern = re.compile(reacciones_pattern, re.IGNORECASE)

    fin = max(t for t, _ in mensajes)
    tramos = [0.0] * (int(fin // ventana) + 1)
    for t, texto in mensajes:
        tramos[int(t // ventana)] += 2 if reacciones_pattern.search(texto) else 1
    return tramos


def buscar_picos(tramos, ventana, cuantos, separacion, minimo):
    """Un pico es un tramo muy por encima de lo normal en los 5 minutos de alrededor."""
    radio = max(1, int(300 // ventana))
    candidatos = []
    for i, v in enumerate(tramos):
        vecinos = tramos[max(0, i - radio): i] + tramos[i + 1: i + 1 + radio]
        normal = statistics.median(vecinos) if vecinos else 0
        fuerza = v / max(normal, 1.0)
        if fuerza >= minimo:
            candidatos.append((fuerza, i, v, normal))
    candidatos.sort(reverse=True)
    elegidos = []
    for fuerza, i, v, normal in candidatos:
        if all(abs(i - j) * ventana >= separacion for _, j, _, _ in elegidos):
            elegidos.append((fuerza, i, v, normal))
        if len(elegidos) == cuantos:
            break
    return sorted(elegidos, key=lambda e: e[1])


def hms(s):
    s = int(max(0, s))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def construir_url_video(vod: str, plataforma="twitch"):
    """Construye la URL del video según la plataforma.

    Args:
        vod: ID del video o URL completa (no puede ser None)
        plataforma: 'twitch', 'youtube' o 'kick'

    Returns:
        URL completa del video

    Raises:
        ValueError: Si vod es None o está vacío
    """
    if not vod:
        raise ValueError(f"ID del video vacío para plataforma {plataforma}")

    # Si ya es una URL, devolverla tal cual
    if vod.startswith("http"):
        return vod

    urls = {
        "twitch": f"https://www.twitch.tv/videos/{vod}",
        "youtube": f"https://www.youtube.com/watch?v={vod}",
        "kick": f"https://kick.com/video/{vod}",
    }

    if plataforma not in urls:
        # Asumir Twitch por defecto
        plataforma = "twitch"

    return urls[plataforma]


def cortar(vod, inicio, fin, salida, plataforma="twitch"):
    """Baja solo ese trozo del directo y lo pasa a vertical 1080x1920 con fondo difuminado."""
    for prog in ("yt-dlp", "ffmpeg"):
        if not shutil.which(prog):
            raise RuntimeError(f"Falta {prog}: instálalo para poder cortar los clips.")

    # Construir URL completa si es necesario
    url = construir_url_video(vod, plataforma)

    bruto = salida + ".bruto.mp4"
    try:
        subprocess.run(
            ["yt-dlp", "-q", "--no-warnings", "-f", "best[height<=1080]",
             "--download-sections", f"*{inicio:.0f}-{fin:.0f}", "--force-keyframes-at-cuts",
             "--merge-output-format", "mp4", "--ignore-config",
             "-o", bruto, "--", url],
            check=True,
            timeout=600,
        )
        filtro = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[fondo];"
            "[0:v]scale=1080:-2[delante];[fondo][delante]overlay=(W-w)/2:(H-h)/2"
        )
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", bruto, "-filter_complex", filtro,
             "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-c:a", "aac", salida],
            check=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Timeout cortando clip (timeout=600s)")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error creando clip: {e}")
    finally:
        if os.path.exists(bruto):
            os.remove(bruto)


def main():
    # Carpeta de clips por defecto: fuera del repo
    default_clips_dir = str(Path.home() / "Clips" / "twitch-clips")

    p = argparse.ArgumentParser(description="Clips de un directo a partir de los picos del chat.")
    p.add_argument("chat", help="chat.json, URL de YouTube/Kick, o URL de Twitch")
    p.add_argument("--vod", help="id del vídeo (si no, se read del chat o URL)")
    p.add_argument("--video-id", dest="video_id", help="alias para --vod")
    p.add_argument("--plataforma", choices=["twitch", "youtube", "kick"],
                   help="twitch, youtube o kick (detectado automáticamente si es posible)")
    p.add_argument("--cortar", action="store_true", help="bajar y cortar los clips en vertical")
    p.add_argument("--clips", type=int, default=10, help="cuántos clips (10)")
    p.add_argument("--ventana", type=int, default=10, help="segundos por tramo (10)")
    p.add_argument("--antes", type=int, help="segundos antes del pico")
    p.add_argument("--despues", type=int, help="segundos después del pico")
    p.add_argument("--minimo", type=float, help="veces por encima de lo normal")
    p.add_argument("--carpeta", default=default_clips_dir,
                   help=f"carpeta de salida (default: {default_clips_dir})")
    a = p.parse_args()

    # Validar --ventana
    if a.ventana < 1:
        sys.exit("Error: --ventana debe ser >= 1")

    # Usar video_id si se proporciona, sino vod
    video_id_arg = a.video_id or a.vod

    # Leer y parsear chat
    try:
        mensajes, vod_chat, plataforma = leer_chat(a.chat, a.plataforma, video_id_arg)
    except ValueError as e:
        sys.exit(f"Error: {e}")
    except FileNotFoundError as e:
        sys.exit(f"Error: Archivo no encontrado: {e}")

    if not mensajes:
        sys.exit("El chat está vacío o no se pudo parsear.")

    # Usar configuración de plataforma si no se especifica
    config = get_platform_config(plataforma)

    # Los parámetros en línea de comandos sobrescriben los defaults de plataforma
    minimo = a.minimo if a.minimo is not None else config["minimo"]
    antes = a.antes if a.antes is not None else config["antes"]
    despues = a.despues if a.despues is not None else config["despues"]
    reacciones = config["reacciones"]

    vod = video_id_arg or vod_chat

    # Analizar chat
    tramos = contar(mensajes, a.ventana, reacciones)
    picos = buscar_picos(tramos, a.ventana, a.clips, separacion=90, minimo=minimo)
    print(f"{len(mensajes)} mensajes · {len(picos)} picos\n")
    if not picos:
        sys.exit("No hay picos claros. Prueba con --minimo 2.")

    if a.cortar:
        if not vod:
            sys.exit("Error: --vod/--video-id requerido para cortar clips.")
        os.makedirs(a.carpeta, exist_ok=True)

    for n, (fuerza, i, v, normal) in enumerate(picos, 1):
        pico = i * a.ventana
        inicio, fin = max(0, pico - antes), pico + a.ventana + despues

        try:
            url = construir_url_video(vod, plataforma)
        except ValueError as e:
            print(f"Error clip {n}: {e}")
            continue

        # Generar enlace con timestamp (formato diferente por plataforma)
        if plataforma == "youtube":
            enlace = f"{url}&t={pico:.0f}s" if vod else ""
        elif plataforma == "kick":
            enlace = url if vod else ""
        else:  # twitch
            h, m, s = pico // 3600, (pico % 3600) // 60, pico % 60
            enlace = f"{url}?t={h}h{m}m{s}s" if vod else ""

        print(f"{n:2d}. {hms(inicio)} → {hms(fin)}  ×{fuerza:.1f} ({v:.0f} frente a {normal:.0f})  {enlace}")

        if a.cortar:
            salida = os.path.join(a.carpeta, f"clip{n:02d}_{hms(pico).replace(':', '-')}.mp4")
            try:
                cortar(vod, inicio, fin, salida, plataforma)
                print(f"    ✅ {salida}")
            except RuntimeError as e:
                print(f"    ❌ Error: {e}")


if __name__ == "__main__":
    main()
