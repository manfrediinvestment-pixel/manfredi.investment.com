"""Genera reports/fci.json: los fondos comunes de inversión más grandes de cada
categoría, con su rendimiento del día, del mes, del año y de 12 meses.

Fuente: planilla diaria pública de CAFCI, leída con la skill cafci
(.claude/skills/cafci/scripts/fetch_cafci.py, de gauss314/skills, MIT).
Lo corre el workflow "Reportes Diarios" todas las mañanas.

Uso: python scripts/build_fci.py
"""
import importlib.util
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(RAIZ, '.claude', 'skills', 'cafci', 'scripts', 'fetch_cafci.py')
SALIDA = os.path.join(RAIZ, 'reports', 'fci.json')
POR_CATEGORIA = 15

# (categoría de CAFCI, clave, nombre para mostrar, moneda)
CATEGORIAS = [
    ('Mercado de Dinero Peso Argentina', 'mm_ars', 'Money market', 'ARS'),
    ('Renta Fija Peso Argentina', 'rf_ars', 'Renta fija', 'ARS'),
    ('Renta Variable Peso Argentina', 'rv_ars', 'Renta variable', 'ARS'),
    ('Renta Mixta Peso Argentina', 'rm_ars', 'Renta mixta', 'ARS'),
    ('Mercado de Dinero Dolar Estadounidense', 'mm_usd', 'Money market USD', 'USD'),
    ('Renta Fija Dolar Estadounidense', 'rf_usd', 'Renta fija USD', 'USD'),
    ('Renta Variable Dolar Estadounidense', 'rv_usd', 'Renta variable USD', 'USD'),
]
HORIZONTE = {'cor': 'corto', 'med': 'mediano', 'lar': 'largo', 'fle': 'flexible'}


def cargar_skill():
    spec = importlib.util.spec_from_file_location('fetch_cafci', SKILL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def redondear(v, n=3):
    return None if v is None else round(float(v), n)


def main():
    cafci = cargar_skill()
    diario = cafci.fetch_diario(use_cache=False)
    fondos = diario.get('fondos') or []
    if not fondos:
        print('CAFCI no devolvió fondos; se deja el archivo anterior.')
        return 1
    salida = {'fecha': diario.get('fecha_reporte'), 'fuente': 'CAFCI', 'categorias': []}
    for cat, clave, nombre, moneda in CATEGORIAS:
        items = [f for f in fondos if f.get('categoria') == cat and (f.get('patrimonio') or 0) > 0 and f.get('variacion_dia_pct') is not None]
        items.sort(key=lambda f: f['patrimonio'], reverse=True)
        salida['categorias'].append({
            'key': clave, 'label': nombre, 'moneda': moneda, 'total': len(items),
            'items': [{
                'nombre': f.get('nombre'),
                'horizonte': HORIZONTE.get(str(f.get('horizonte') or '').lower()[:3], None),
                'vcp': redondear(f.get('vcp_actual'), 4),
                'dia': redondear(f.get('variacion_dia_pct')),
                'mes': redondear(f.get('variacion_mes_pct')),
                'ytd': redondear(f.get('variacion_ytd_pct')),
                'anual': redondear(f.get('variacion_12m_pct')),
                'patrimonio': round(f.get('patrimonio') or 0),
                'moneda': f.get('moneda') or moneda,
            } for f in items[:POR_CATEGORIA]],
        })
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, 'w', encoding='utf-8') as fh:
        json.dump(salida, fh, ensure_ascii=False, separators=(',', ':'))
    print('fci.json:', salida['fecha'], ', '.join(f"{c['label']} {len(c['items'])}" for c in salida['categorias']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
