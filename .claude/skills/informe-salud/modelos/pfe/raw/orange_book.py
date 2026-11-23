# Fechas de patente y exclusividad de los productos de Pfizer en el Orange Book de la FDA.
# Bajar antes (no se versiona, pesa ~9 MB): https://www.fda.gov/media/76860/download?attachment -> descomprimir en ob/
# (products.txt, patent.txt, exclusivity.txt). Guarda el extracto en ob_pfe.json (sí se versiona).
# Uso: python orange_book.py [carpeta_ob]
import csv, collections, json, os, sys, datetime as dt
os.chdir(os.path.dirname(os.path.abspath(__file__)))
OB = sys.argv[1] if len(sys.argv) > 1 else 'ob'
rd = lambda f: list(csv.DictReader(open(f'{OB}/{f}.txt', encoding='latin-1'), delimiter='~'))
prod, pat, exc = rd('products'), rd('patent'), rd('exclusivity')
NAMES = ['ELIQUIS', 'IBRANCE', 'XTANDI', 'XELJANZ', 'XELJANZ XR', 'VYNDAQEL', 'VYNDAMAX', 'INLYTA', 'LORBRENA', 'NURTEC ODT',
         'PAXLOVID', 'BRAFTOVI', 'MEKTOVI', 'TALZENNA', 'TUKYSA', 'BOSULIF', 'CIBINQO', 'LITFULO', 'VELSIPITY', 'ORGOVYX', 'XALKORI']
def ymd(s): return dt.datetime.strptime(s, '%b %d, %Y').strftime('%Y-%m-%d')
appl = collections.defaultdict(set)
for p in prod:
    if p['Trade_Name'] in NAMES and p['Type'] == 'RX':
        appl[p['Trade_Name']].add((p['Appl_No'], p['Applicant'], p['Approval_Date']))
out = {}
for n in NAMES:
    a = appl.get(n)
    if not a: out[n] = None; print(n, '| no está'); continue
    nos = {x[0] for x in a}
    pp = sorted({(ymd(r['Patent_Expire_Date_Text']), r['Patent_No'], r['Drug_Substance_Flag'], r['Drug_Product_Flag'], r['Patent_Use_Code'])
                 for r in pat if r['Appl_No'] in nos})
    ee = sorted({(ymd(r['Exclusivity_Date']), r['Exclusivity_Code']) for r in exc if r['Appl_No'] in nos})
    sub = sorted({x[0] for x in pp if x[2] == 'Y'}); prd = sorted({x[0] for x in pp if x[3] == 'Y'})
    out[n] = dict(nda=sorted(nos), aprobacion=sorted({x[2] for x in a})[0], sustancia=sub, producto_ultima=prd[-1] if prd else None,
                  ultima=pp[-1][0] if pp else None, exclusividades=ee)
    print(f"{n} | NDA {','.join(sorted(nos))} | sustancia {sub} | producto(últ.) {out[n]['producto_ultima']} | última {out[n]['ultima']} | excl {ee[-3:]}")
meta = dict(fuente='FDA Orange Book, archivo de datos (https://www.fda.gov/media/76860/download?attachment)',
            fecha_archivo=dt.datetime.fromtimestamp(os.path.getmtime(f'{OB}/patent.txt')).strftime('%Y-%m-%d'))
json.dump(dict(meta=meta, productos=out), open('ob_pfe.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
