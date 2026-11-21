# 🎬 Twitch Clip Extractor

> Automatically extract the best moments from your Twitch VODs by analyzing chat activity in real-time.

**Generate vertical clips (1080x1920) ready for TikTok, Instagram Reels and YouTube Shorts.**

---

## ✨ Features

- 🤖 **Automatic chat analysis** - Detects emotion peaks in chat
- 📱 **Vertical format** - 1080x1920 perfect for social media
- ⚡ **Fast and efficient** - Processes streams of any duration
- 🎯 **Customizable** - Adjust sensitivity, clip count, and duration
- 📊 **Data-driven** - Uses real chat reactions as indicators
- 🔧 **Twitch-focused** - Full support for Twitch VODs

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Emperador24/twitch-clip-extractor.git
cd twitch-clip-extractor

# Install dependencies (macOS)
brew install python yt-dlp ffmpeg

# Download TwitchDownloaderCLI
# Go to: https://github.com/lay295/TwitchDownloader/releases
# Download the version for your system and place it in the project folder
```

### 2. Generate clips (3 steps)

```bash
# Step 1: Download chat from VOD
./TwitchDownloaderCLI chatdownload --id 1234567890 -o chat.json

# Step 2: View peaks (preview)
python3 clipear.py "https://www.twitch.tv/videos/1234567890" --sin-cortar

# Step 3: Generate clips
python3 clipear.py "https://www.twitch.tv/videos/1234567890" --clips 10
```

Clips are saved in `./clips/` ✅

---

## 📋 Requirements

- Python 3.9+
- macOS, Linux or WSL
- 2GB free space (per clip)

| Component | Install |
|-----------|---------|
| **yt-dlp** | `brew install yt-dlp` |
| **ffmpeg** | `brew install ffmpeg` |
| **TwitchDownloaderCLI** | [Download](https://github.com/lay295/TwitchDownloader/releases) |

---

## 🎯 Usage

### Basic usage

```bash
python3 clipear.py "https://www.twitch.tv/videos/STREAM_ID"
```

### With options

```bash
# Generate 5 clips instead of 10
python3 clipear.py "URL" --clips 5

# Adjust sensitivity (lower = more clips)
python3 clipear.py "URL" --minimo 2.0

# Only show peaks without downloading videos (fast)
python3 clipear.py "URL" --sin-cortar

# Combined options
python3 clipear.py "URL" --clips 20 --minimo 2.5
```

### Parameters

```
--clips N       Number of clips to generate (default: 10)
--minimo N      Detection sensitivity (default: 3.0)
                - 1.5: very sensitive (many clips)
                - 3.0: normal
                - 5.0: very selective (few clips)
--sin-cortar    Only show peaks without processing videos
```

---

## 🔧 How It Works

### 1. **Chat Analysis**
Reads downloaded chat JSON and counts messages per second.

### 2. **Peak Detection**
Identifies moments where activity **exceeds 3x the median** of the last 5 minutes.

### 3. **Reactions**
Doubles the count for messages with reactions:
- Laughs: `jaja`, `xd`, `kekw`, `lul`, `omegalul`, `lmao`
- Emojis: `😂` `🤣` `💀`
- Others: `clip`, `pog`, `wtf`, `noo`

### 4. **Clip Generation**
- Downloads the video segment
- Adapts to vertical format with blurred background
- Encodes with H.264 quality

---

## 📊 Default Configuration

```python
minimo = 3.0          # Sensitivity
antes = 20            # Seconds before peak
despues = 15          # Seconds after peak
ventana = 10          # Analysis every 10 seconds
```

---

## ⏱️ Expected Time

| Action | Time |
|--------|------|
| View peaks | 1-2 sec |
| Download chat | 10-30 sec |
| Per clip | 2-5 min |
| **10 clips** | **20-50 min** |

---

## 📂 Structure

```
twitch-clip-extractor/
├── clipear.py              # Main script
├── clips_chat.py           # Chat analysis
├── config.py               # Configuration
├── parsers/                # Chat parsers
│   ├── base.py
│   └── twitch.py
├── TwitchDownloaderCLI     # Tool for downloading chat
├── clips/                  # Output folder
└── README.md               # This guide
```

---

## 🎓 Examples

### Example 1: Generate 5 clips from a VOD

```bash
# Get the VOD ID: https://www.twitch.tv/videos/2932415021
# ID: 2932415021

./TwitchDownloaderCLI chatdownload --id 2932415021 -o chat.json
python3 clipear.py "https://www.twitch.tv/videos/2932415021" --clips 5
```

**Result:** 5 clips in `./clips/` ready to upload

---

### Example 2: More selective clips

```bash
# High sensitivity (fewer clips, better quality)
python3 clipear.py "URL" --clips 10 --minimo 4.5
```

---

### Example 3: Preview before generating

```bash
# View peaks without downloading
python3 clipear.py "URL" --sin-cortar

# If you like them, generate:
python3 clipear.py "URL" --clips 10 --cortar
```

---

## 🐛 Troubleshooting

### "TwitchDownloaderCLI not found"
```bash
# Download from: https://github.com/lay295/TwitchDownloader/releases
# Extract in the project folder
chmod +x TwitchDownloaderCLI
```

### "No clear peaks"
```bash
# Reduce sensitivity
python3 clipear.py "URL" --minimo 2.0
```

### "ffmpeg not found"
```bash
brew install ffmpeg
```

### "Chat is empty"
The VOD might:
- Be very old (Twitch deleted the chat)
- Have chat disabled
- Not have chat replay available

**Solution:** Find a more recent VOD

---

## 📝 Notes

- ✅ **Twitch:** Works perfectly with VODs
- ❌ **YouTube:** Chat not always available in VODs
- ❌ **Kick:** Very limited public chat
- 📱 **Format:** Always vertical (1080x1920)
- 🎨 **Background:** Blurred automatically
- 📊 **Quality:** H.264 codec, CRF 20

---

## 📄 License

This project is open source. **Use it only with creators who allow clips of their streams.**

---

## 🤝 Contributing

Ideas? Improvements? Open an issue or PR.

---

## 👨‍💻 Author

Created with ❤️ for content creators

---

## 🔗 Useful Links

- [TwitchDownloader](https://github.com/lay295/TwitchDownloader) - Download chat
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download videos
- [FFmpeg](https://ffmpeg.org/) - Video processing

---

## ⭐ If this was helpful, leave a star!

```
git clone https://github.com/Emperador24/twitch-clip-extractor.git
```
