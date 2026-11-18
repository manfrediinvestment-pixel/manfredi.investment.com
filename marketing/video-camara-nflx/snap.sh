#!/usr/bin/env bash
# Cuadros de control: bash snap.sh <clip> <t1,t2,...>
set -e
cd "$(dirname "$0")"
cp comun/base.css comun/charts.js hyperframes.json "$1/"
npx --yes hyperframes@0.7.109 snapshot "$1" --at "$2" --no-end --describe false -o "snaps/$1"
