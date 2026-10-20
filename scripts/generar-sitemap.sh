#!/bin/sh
# Regenera sitemap.xml con la home, la bienvenida y todos los informes.
# Las URLs van sin .html porque Cloudflare redirige (308) /x.html -> /x.
# lastmod = fecha del último commit que tocó cada archivo.
# Uso (desde la raíz del repo): sh scripts/generar-sitemap.sh
BASE="https://manfredinvestment.com"
fecha() { d=$(git log -1 --format=%cs -- "$1"); [ -n "$d" ] && echo "$d" || date +%F; }
url() { printf '  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n' "$1" "$2"; }
{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  url "$BASE/" "$(fecha index.html)"
  url "$BASE/bienvenida" "$(fecha bienvenida.html)"
  for f in informes/*.html; do
    url "$BASE/${f%.html}" "$(fecha "$f")"
  done
  echo '</urlset>'
} > sitemap.xml
echo "sitemap.xml: $(grep -c '<url>' sitemap.xml) URLs"
