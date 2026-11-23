# Compara informes/pfe.html contra model.json. Sale con código 1 si hay diferencias.
import json, re, sys, subprocess, shutil
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4].as_posix()   # raíz del repo
M = json.load(open(HERE / 'model.json', encoding='utf-8'))
src = open(HERE / 'render.py', encoding='utf-8').read().split('src = open(sys.argv[1]')[0]
ns = {}; exec(src.replace("open('model.json'", "open(r'" + str(HERE / 'model.json') + "'"), ns); fmt, get = ns['fmt'], ns['get']
tpl = open(HERE / 'pfe.full.tpl.html', encoding='utf-8').read()
out = open(ROOT + '/informes/pfe.html', encoding='utf-8').read()
diffs = []
# 1) cada token de la plantilla aparece en el HTML con el valor del modelo, en su lugar
parts = re.split(r'(\{\{[^}]+\}\})', tpl); pattern = ''; tokens = []
for p in parts:
    m = re.fullmatch(r'\{\{([^|}]+)\|?([^}]*)\}\}', p)
    if m: pattern += '(.*?)'; tokens.append((m.group(1).strip(), m.group(2)))
    else: pattern += re.escape(p)
mm = re.fullmatch(pattern, out, re.S)
if not mm: diffs.append('el HTML no respeta la estructura de la plantilla (texto editado a mano)')
else:
    for (k, f), got in zip(tokens, mm.groups()):
        exp = fmt(get(k), f)
        if got != exp: diffs.append(f'{k}: HTML={got!r} modelo={exp!r}')
print('tokens verificados:', len(tokens))
# 2) aritmética del blend leída del propio HTML
def money(s): return float(s.replace('$', '').replace(',', '').replace('−', '-'))
rows = re.findall(r'<td class="label">Método (\d)[^<]*</td><td class="label">[^<]*</td><td class="right-al">([^<]+)</td><td class="right-al">(\d+)%</td><td class="right-al">([^<]+)</td>', out)
tot = 0
for n, fv, w, ap in rows:
    calc = money(fv) * int(w) / 100
    if abs(calc - money(ap)) > 0.006: diffs.append(f'aporte método {n}: {ap} vs {calc:.2f}')
    tot += calc
if len(rows) != 4: diffs.append(f'filas de métodos leídas: {len(rows)}')
blend = money(re.search(r'<div class="fv-value">([^<]+)</div>', out).group(1))
if abs(tot - blend) > 0.011: diffs.append(f'blend portada {blend} vs suma de aportes {tot:.4f}')
gap = re.search(r'vs\. \$[\d.,]+ mercado · ([^<]+)</div>', out).group(1)
if gap != fmt((blend / M['price'] - 1) * 100, 'spct1'): diffs.append(f'gap portada {gap}')
if ('fv-gap pos' in out) != (blend > M['price']): diffs.append('clase pos/neg del gap')
if len(re.findall(r'class="fv-value"', out)) != 1: diffs.append('la portada debe tener un solo fair value')
# 3) celda Base de la grilla = Método 1; suma de partes
cell = re.search(r'base-cell">([^<]+)</td>', out).group(1)
if cell != fmt(M['m1'], 'usd2'): diffs.append(f'celda base: {cell}')
S = M['sotp']
if abs(sum(S.values()) - M['m1_ev']) > 1e-9 or abs((M['m1_ev'] - M['net_debt']) / M['shares_dil'] - M['m1']) > 1e-9: diffs.append('suma de partes')
if abs(M['grid'][2][M['grid_base_col']] - M['m1']) > 1e-9 or M['grid_base_col'] != 2: diffs.append('grilla: la columna Base debe ser la del medio')
# 4) grupos independientes / anclados recalculados desde el HTML
fv = {n: money(v) for n, v, w, a in rows}
ind = (0.15 * fv['1'] + 0.25 * fv['2']) / 0.40; anc = (0.35 * fv['3'] + 0.25 * fv['4']) / 0.60
if fmt(ind, 'usd2') not in out or fmt(anc, 'usd2') not in out: diffs.append('promedios de grupo')
# 5) anti-circularidad: con el precio de PFE 25% más alto, los cuatro métodos no cambian; M2 = mediana x EPS 2027 / (1 + Ke)
for k in ('anti_m1', 'anti_m2', 'anti_m3', 'anti_m4'):
    if M[k] != 0: diffs.append(k)
if abs(M['m2'] - M['peer_med'] * M['c27'] / (1 + M['ke'] / 100)) > 1e-9: diffs.append('Método 2 no es mediana x EPS 2027 descontado')
if abs(M['peer_med'] - 15.766) > 1e-9: diffs.append('mediana de pares distinta de la del research común')
# 6) deuda: corto + largo del 10-Q, sin duplicar; cuadro comparativo armado por el modelo
if abs(M['debt'] - (2.674 + 59.997)) > 1e-9: diffs.append('deuda total')
sys.path.insert(0, str(HERE)); from cmp_table import table_html, KEYS
tab, has_abbv = table_html(M)
if tab not in out: diffs.append('cuadro PFE/ABBV/LLY/JNJ distinto del que arma cmp_table.py')
if list(M['cmp']) != KEYS: diffs.append('claves de cmp')
if abs(M['cmp']['fair_value'] - blend) > 0.006 or M['cmp']['postura'] != M['postura']: diffs.append('cmp no coincide con la portada')
print('cuadro comparativo con ABBV:', has_abbv)
# 7) reglas de texto y del sitio
vis = re.sub(r'(?is)<(script|style).*?</\1>', '', out)
for w in re.findall(r'\b(hoy|ayer|mañana|actualmente|recientemente|este año|el año pasado|la semana pasada|este mes)\b|hace \d+ (?:hora|día|mes|año)', vis, re.I): diffs.append(f'lenguaje relativo: {w}')
if out.count('<script src="_preview-gate.js" defer></script>') != 1: diffs.append('falta el gate')
if 'src="../assets/logos/pfe.png"' not in out: diffs.append('falta el logo')
if '{{' in out or '@@' in out: diffs.append('tokens sin reemplazar')
if re.search(r'#5d646f|#6b7280|#9ca3af|#888|#999|#777|#666|#aaa|color:\s*gr[ae]y|\bgr[ae]y\b', out, re.I): diffs.append('texto gris')
if 'Datos al 3T 2026 (cierre 27 sep 2026, publicado 3 nov 2026)' not in out: diffs.append('cabecera')
if len(re.findall(r'<p class="secnum" id="s\d\d">', out)) != 14: diffs.append('cantidad de secciones')
# 8) cada gráfico tiene canvas y llamada con datos; el JS parsea (node --check)
canv = re.findall(r'<canvas id="(\w+)"', out)
for c in canv:
    if f"getElementById('{c}')" not in out: diffs.append(f'gráfico sin datos: {c}')
js = re.findall(r'(?s)<script>(.*?)</script>', out)
if shutil.which('node'):
    p = HERE / '_check.js'; p.write_text('\n'.join(js), encoding='utf-8')
    r = subprocess.run(['node', '--check', str(p)], capture_output=True, text=True); p.unlink()
    if r.returncode: diffs.append('error de sintaxis JS: ' + r.stderr[:300])
print('gráficos:', len(canv))
print('diferencias:', len(diffs))
for d in diffs: print(' -', d)
sys.exit(1 if diffs else 0)
