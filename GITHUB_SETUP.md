# 🚀 Cómo subir a GitHub

## Paso 1: Crear repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. Nombre del repositorio: `twitch-clip-extractor`
3. Descripción: `Extrae automáticamente clips de VODs de Twitch analizando el chat`
4. Visibilidad: **Public** (para que otros lo vean)
5. NO hagas nada más (no inicialices con README)
6. Click en "Create repository"

---

## Paso 2: Conectar el repositorio local

Después de crear, GitHub te mostrará comandos. Ejecuta estos en tu terminal:

```bash
cd /Users/samuel/Documents/Clips

# Cambiar rama a "main" (opcional pero recomendado)
git branch -M main

# Agregar remoto
git remote add origin https://github.com/TU_USUARIO/twitch-clip-extractor.git

# Subir código
git push -u origin main
```

**Reemplaza `TU_USUARIO` con tu username de GitHub**

---

## Paso 3: Verificar

Ve a `https://github.com/TU_USUARIO/twitch-clip-extractor` y verás:
- ✅ Código
- ✅ README.md profesional
- ✅ Licencia MIT
- ✅ .gitignore

---

## 📝 Futuras actualizaciones

Cuando hagas cambios:

```bash
# En la carpeta del proyecto
git add .
git commit -m "Descripción del cambio"
git push
```

---

## ⭐ Opcionales pero recomendados

### Agregar temas (topics)
En la página del repositorio → About → Add topics:
- `twitch`
- `clip-extractor`
- `vod`
- `automation`
- `python`
- `social-media`

### Agregar descripción corta
En About:
> Extrae automáticamente clips de VODs de Twitch analizando picos de actividad del chat. Genera videos verticales listos para TikTok, Reels y Shorts.

### Agregar enlace útil
En About → Website: 
(opcional, puedes dejar en blanco)

---

## 🎯 Resultado final

Tu repositorio será:
- ✅ Visible en GitHub
- ✅ Fácil de encontrar
- ✅ Profesional
- ✅ Listo para clonar: `git clone https://github.com/TU_USUARIO/twitch-clip-extractor.git`

---

## 💡 Tips

- Mantén el README actualizado
- Usa issues para bugs
- Considera usar releases para versiones
- Agrega ejemplos en la wiki

¡Listo! 🚀
