# 🚀 Inicio rápido

## Instalación (primera vez)

```bash
# 1. Instalar dependencias del sistema
brew install python yt-dlp ffmpeg

# 2. Descargar TwitchDownloaderCLI (para Twitch)
# Ve a: https://github.com/lay295/TwitchDownloader/releases
# Descarga la versión para Mac y extrae el archivo
```

## Primer clip en 3 pasos

### Opción A: Twitch (lo que ya hacías)

```bash
# Paso 1: Descargar chat
./TwitchDownloaderCLI chatdownload --id 1234567890 -o chat.json

# Paso 2: Ver picos
python3 clips_chat.py chat.json --vod 1234567890

# Paso 3: Crear clips (requiere 100MB+ espacio libre y ~1-5 min por clip)
python3 clips_chat.py chat.json --vod 1234567890 --cortar
```

Los clips se guardan en carpeta `./clips/`

### Opción B: YouTube (nuevo)

```bash
# Todo automático - solo pasa la URL
python3 clips_chat.py "https://www.youtube.com/watch?v=abc123xyz" --cortar
```

### Opción C: Kick (nuevo)

```bash
# También automático
python3 clips_chat.py "https://kick.com/video/xyz789" --cortar
```

## Próximos pasos

- Lee [README.md](README.md) para ver todas las opciones
- Ajusta `--minimo` si detecta muy pocos o demasiados picos
- Usa `--clips 5` para menos clips, `--clips 20` para más

## Notas

- **YouTube**: el chat se descarga automáticamente (algunos videos no tienen chat disponible)
- **Kick**: algunos videos pueden no tener chat público
- **Twitch**: igual que antes, pero ahora también soporta URLs directas

## Archivo de ejemplo

Para probar sin descargar nada:

```bash
python3 clips_chat.py example_twitch_chat.json --vod 123456789
```

Esto debería mostrar 3 picos detectados.
