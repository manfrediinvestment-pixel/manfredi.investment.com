#!/usr/bin/env bash
# Renderiza los clips 16:9 del video a cámara de NFLX.
# Uso: bash render.sh [clip...]   (sin args: todos). Salida: salida/<clip>.mp4
set -e
cd "$(dirname "$0")"
CLIPS=${@:-"gancho seccion-1 seccion-2 seccion-3"}
mkdir -p salida
for c in $CLIPS; do
  cp comun/base.css comun/charts.js "$c/"
  cp hyperframes.json "$c/"
  npx --yes hyperframes@0.7.109 render "$c" -o "salida/$c.mp4" -q high --quiet
done
