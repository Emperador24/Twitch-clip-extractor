# 🎬 clipear.py - La forma más fácil

Solo necesitas **pasarme el link** del directo. ¡Listo!

## 🚀 Uso ultra simple

```bash
python3 clipear.py "https://www.twitch.tv/videos/123456789"
python3 clipear.py "https://www.youtube.com/watch?v=abc123xyz"
python3 clipear.py "https://kick.com/video/xyz789"
```

## ¿Dónde obtengo el link?

### Twitch
1. Abre twitch.tv
2. Ve al canal del creador
3. Haz clic en la miniatura del directo que quieres
4. Copia la URL: `https://www.twitch.tv/videos/123456789`

### YouTube
1. Abre youtube.com
2. Busca el video
3. Copia la URL: `https://www.youtube.com/watch?v=abc123xyz`

### Kick
1. Abre kick.com
2. Busca el video
3. Copia la URL: `https://kick.com/video/xyz789`

## ⚙️ Opciones

```bash
# Menos clips (default es 10)
python3 clipear.py "<URL>" --clips 5

# Más sensibilidad (default según plataforma)
python3 clipear.py "<URL>" --minimo 2.0

# Solo ver picos sin descargar videos
python3 clipear.py "<URL>" --sin-cortar

# Combinadas
python3 clipear.py "<URL>" --clips 20 --minimo 2.5
```

## 📊 Parámetros

### `--clips N`
Cuántos clips generar (default: 10)
- 5 = clips más selectos
- 10 = balance
- 20 = más cantidad

### `--minimo N`
Sensibilidad para detectar picos (default: según plataforma)
- 1.5 = muy sensible (muchos clips)
- 3.0 = normal (Twitch default)
- 5.0 = muy selectivo (pocos clips)

### `--sin-cortar`
Solo muestra dónde están los picos, sin descargar videos (rápido)

## ⏱️ Tiempo esperado

| Acción | Tiempo |
|--------|--------|
| Ver picos | 1-2 seg |
| Descargar chat (Twitch) | 10-30 seg |
| Por cada clip | 2-5 min |

**Total para 10 clips:** ~20-50 minutos

## 📂 Dónde quedan los clips

Los clips se guardan en: `./clips/clip01_*.mp4`, `./clips/clip02_*.mp4`, etc.

## ❓ Preguntas frecuentes

**¿Qué pasa si el directo es muy largo?**
→ Toma más tiempo. Para directos > 2 horas, usa `--clips 5` para ir más rápido.

**¿Se puede bajar de sensibilidad?**
→ Sí, con `--minimo 2.0` detecta más picos (pero algunos pueden no ser buenos).

**¿Qué pasa si falla?**
→ Si falla descargando chat de Twitch: verifica que TwitchDownloaderCLI esté instalado.

## 🎯 Ejemplo completo

```bash
# Generar 5 clips de un directo de Twitch
python3 clipear.py "https://www.twitch.tv/videos/1234567890" --clips 5

# Generar 15 clips de YouTube con sensibilidad baja
python3 clipear.py "https://www.youtube.com/watch?v=abc123xyz" --clips 15 --minimo 2.0

# Solo ver picos sin descargar (para verificar)
python3 clipear.py "https://kick.com/video/xyz789" --sin-cortar
```

---

¡Eso es todo! Solo pasa el link y el script se encarga del resto. 🚀
