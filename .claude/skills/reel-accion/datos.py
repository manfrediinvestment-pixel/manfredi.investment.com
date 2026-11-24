# Datos de base para un reel de acción.
# Uso (desde la raíz del repo):  python -I .claude/skills/reel-accion/datos.py <ticker> <carpeta_salida>
# Escribe en <carpeta_salida>/datos/:
#   informe.txt  -> texto plano del informe (informes/<ticker>.html), para leerlo entero
#   precio.json  -> cierres diarios de 1 año (Yahoo Finance) + máximo, mínimo, último, var. y los saltos de un día
import json, pathlib, re, html, sys
import yfinance as yf

t = sys.argv[1].lower()
out = pathlib.Path(sys.argv[2]) / "datos"
out.mkdir(parents=True, exist_ok=True)
root = pathlib.Path.cwd()

src = (root / "informes" / f"{t}.html").read_text(encoding="utf-8")
src = re.sub(r"<(script|style)[\s\S]*?</\1>", "", src)
txt = html.unescape(re.sub(r"<[^>]+>", " ", src))
txt = re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t]+", " ", txt))
(out / "informe.txt").write_text(txt, encoding="utf-8")

sym = t.upper().replace(".", "-")           # brk.b -> BRK-B
d = yf.Ticker(sym).history(period="1y", interval="1d", auto_adjust=False)["Close"].dropna()
fechas = [i.strftime("%Y-%m-%d") for i in d.index]
px = [round(float(v), 2) for v in d.values]
imax = max(range(len(px)), key=lambda i: px[i]); imin = min(range(len(px)), key=lambda i: px[i])
saltos = sorted(({"fecha": fechas[i], "i": i, "de": px[i-1], "a": px[i], "var": round(px[i]/px[i-1]-1, 4)}
                 for i in range(1, len(px))), key=lambda s: -abs(s["var"]))[:8]
res = {
    "ticker": sym, "desde": fechas[0], "hasta": fechas[-1], "n": len(px),
    "primero": px[0], "ultimo": px[-1], "var_1a": round(px[-1]/px[0]-1, 4),
    "max": {"fecha": fechas[imax], "i": imax, "px": px[imax]},
    "min": {"fecha": fechas[imin], "i": imin, "px": px[imin]},
    "var_desde_max": round(px[-1]/px[imax]-1, 4),
    "saltos_1d": saltos,          # los días que más se movió: buscar QUÉ pasó ese día (gancho / sección)
    "fechas": fechas, "px": px,
}
(out / "precio.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in res.items() if k not in ("fechas", "px")}, ensure_ascii=False, indent=1))
print("informe.txt:", len(txt), "caracteres")
