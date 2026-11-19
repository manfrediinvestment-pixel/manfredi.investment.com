#!/usr/bin/env bash
# Después del cierre: rellena con el precio final, renderiza todo y copia al Escritorio.
set -e
cd "$(dirname "$0")"
python rellenar.py ../../../manfredi-informe-ant/.claude/skills/informe-bigtech/modelos/ant/resultados.json
bash render.sh
D="/c/Users/Equipo/Desktop/Video reels/ANT a camara"; mkdir -p "$D"
for c in gancho seccion-1 seccion-2 seccion-3 cierre; do
  cp "salida/$c.mp4" "$D/"
  ffmpeg -y -loglevel error -ss 4.7 -i "salida/$c.mp4" -frames:v 1 "$D/$c-A.png"
  ffmpeg -y -loglevel error -sseof -0.1 -i "salida/$c.mp4" -frames:v 1 "$D/$c-B.png"
done
cp GUION.md "$D/"
for c in gancho seccion-1 seccion-2 seccion-3 cierre; do ffprobe -v error -show_entries format=duration -of csv=p=0 "salida/$c.mp4" | xargs echo "$c"; done
