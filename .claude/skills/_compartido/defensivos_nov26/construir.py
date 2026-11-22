# Ensambla ../defensivos_nov26.json (research común de COST, PFE y ABBV). Orden: python fetch_mercado.py; python fetch_sa.py;
# python mercado.py; python construir.py. Cada dato lleva fuente y fecha. Fecha de corte de mercado: viernes 20-nov-2026.
import json, re, statistics as st, datetime
import numpy as np

M = json.load(open('mercado.json', encoding='utf-8'))
T = M['tickers']; CUT = M['fecha_cierre']


def sa_cell(t, label):
    h = open(f'sa/{t}.statistics.html', encoding='utf-8').read()
    m = re.search(r'<span><!---->' + re.escape(label) + r'<!---->.*?title="([^"]*)"', h, re.S)
    return m.group(1) if m else None


def bnum(s):
    """'5.70B' -> 5.70 (miles de millones)."""
    if s in (None, 'n/a', '-'): return None
    s = s.replace(',', '').replace('$', '')
    mult = {'T': 1e3, 'B': 1, 'M': 1e-3}.get(s[-1])
    return float(s[:-1]) * mult if mult else float(s) / 1e9


for t in T:
    sh = bnum(sa_cell(t, 'Shares Outstanding')); debt = bnum(sa_cell(t, 'Total Debt')); nc = bnum(sa_cell(t, 'Net Cash'))
    mc = sh * T[t]['cierre_20nov'] if sh else None
    T[t]['balance_sa'] = dict(
        acciones_mm=round(sh * 1000, 1) if sh else None,
        deuda_total_usd_mm=round(debt * 1000) if debt is not None else None,
        caja_neta_usd_mm=round(nc * 1000) if nc is not None else None,
        mcap_usd_mm=round(mc * 1000) if mc else None,
        d_sobre_v=round(debt / (debt + mc), 4) if (debt is not None and mc) else None,
        fuente='stockanalysis.com /statistics (último balance reportado), bajado 22-nov-2026; mcap = acciones x cierre 20-nov')

F_SA = 'stockanalysis.com (/forecast y /statistics), consenso de S&P Global; bajado el 22-nov-2026 (sin sesiones desde el cierre del 20-nov)'
F_YH = 'Yahoo Finance chart API v8, cierre diario; bajado 22-nov-2026'
RF = M['indices']['^TNX']; ERP = 5.0
FS_PX = 7175.83; GSPC = M['indices']['^GSPC']


def chg(t, a, b):
    d = json.load(open(f'yh/{t}.d.json'))['chart']['result'][0]
    r = {datetime.datetime.fromtimestamp(x, datetime.UTC).date().isoformat(): c
         for x, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c}
    return r[b] / r[a]


# ---------------- Mercado general ----------------
mercado = dict(
    fecha_cierre=CUT,
    treasury_10y=dict(valor_pct=RF, fuente=F_YH + ' (^TNX)', fecha=CUT),
    prima_riesgo=dict(
        erp_casa_pct=ERP, nota='ERP fija de la casa (skills informe-bigtech/salud/consumo; misma que WMT, JNJ y LLY)',
        erp_damodaran_pct=4.41, erp_damodaran_fecha='2026-11-01', erp_damodaran_base='trailing 12m con payout ajustado; rf usada 4.94%',
        erp_damodaran_variantes=dict(cash_yield=3.79, promedio_cf_10a=5.81, net_cash_yield=3.43, normalizada=3.39),
        fuente='https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm (leído 22-nov-2026)',
        uso='La valuación usa 5.0% (casa). 4.41% se reporta como sensibilidad, igual que WMT (erp_dam).'),
    sp500=dict(
        cierre_20nov=GSPC, cierre_19nov_factset=FS_PX, caida_20nov_pct=round((GSPC / FS_PX - 1) * 100, 2),
        pe_fwd_factset=17.1, pe_fwd_5a=19.8, pe_fwd_10a=19.1, pe_ttm_factset=22.9,
        pe_fwd_ajustado_20nov=round(17.1 * GSPC / FS_PX, 2),
        nota='FactSet usa el cierre del 19-nov (7,175.83). El 20-nov el S&P cayó 3.7%; pe_fwd_ajustado_20nov = 17.1 x 6,910.39 / 7,175.83 con EPS constante. Usar el ajustado para el P/E relativo al cierre del 20-nov y declarar los dos.',
        fuente='FactSet Earnings Insight 20-nov-2026, págs. 1, 12 y 26 (EarningsInsight_112026.pdf)'),
    sectores_pe_fwd=dict(
        consumer_staples=dict(pe_fwd=23.3, prom_5a=20.9, prom_10a=20.2, pe_ajustado_20nov=round(23.3 * chg('XLP', '2026-11-19', CUT), 2)),
        health_care=dict(pe_fwd=18.8, prom_5a=17.5, prom_10a=16.7, pe_ajustado_20nov=round(18.8 * chg('XLV', '2026-11-19', CUT), 2)),
        nota='Ajuste al 20-nov por la variación de XLP / XLV del 19 al 20-nov (Yahoo), EPS constante.',
        fuente='FactSet Earnings Insight 20-nov-2026, pág. 26, "S&P 500 Sector-Level Forward 12-Month P/E Ratios"'),
    sector_etf_cierre_20nov=dict(XLP=M['indices']['XLP'], XLV=M['indices']['XLV'], SPY=M['indices']['SPY']),
)

# ---------------- Consenso: misma fuente y mismo día para los tres ----------------
consenso = dict(
    fuente=F_SA, fecha_precio=CUT,
    tickers={t: dict(T[t]['consenso'], cierre_20nov=T[t]['cierre_20nov']) for t in ('COST', 'PFE', 'ABBV')},
    nota='Usar ESTE pt_prom en el Método 4 de los tres informes. La página gratis no da el desglose por categoría de recomendación.')

# ---------------- Pharma común ----------------
PEERS_PH = ['LLY', 'JNJ', 'MRK', 'BMY', 'AMGN', 'GILD', 'NVO', 'AZN', 'NVS', 'GSK', 'SNY', 'REGN', 'VRTX']
peers = {}
for t in PEERS_PH:
    c = T[t]['consenso']; mu = T[t]['multiplos']
    peers[t] = dict(
        cierre_20nov=T[t]['cierre_20nov'],
        **{k: mu[k] for k in ('pe_fwd', 'peg', 'ev_ebitda', 'beta_5y', 'div_yield_pct', 'roic_pct', 'deuda_ebitda')},
        eps_fy26=c.get('eps_ajustado_fy_actual'), eps_fy27=c.get('eps_ajustado_fy_siguiente'),
        pe_fy27=round(T[t]['cierre_20nov'] / c['eps_ajustado_fy_siguiente'], 3) if c.get('eps_ajustado_fy_siguiente') else None,
        d_sobre_v=T[t]['balance_sa']['d_sobre_v'], pt_prom=c['pt_prom'], n_analistas=c['n_analistas'], recomendacion=c['recomendacion'])
for t in ('NVO', 'AZN', 'NVS', 'GSK', 'SNY'):
    peers[t]['nota_adr'] = 'ADR: el EPS de consenso puede venir en moneda local o por acción ordinaria (NVO 22.8 es en DKK); usar pe_fwd de stockanalysis, no cierre/eps.'
for t in ('MRK', 'GILD'):
    peers[t]['nota_eps'] = 'EPS FY2026 de consenso deprimido por IPR&D adquirida dentro del no-GAAP (MRK ~2.79, GILD negativo): no usar FY2026; usar FY2027 o pe_fwd.'

B_RAW = st.mean(peers[t]['beta_5y'] for t in PEERS_PH); B_BL = 0.67 * B_RAW + 0.33
DV = st.median(peers[t]['d_sobre_v'] for t in PEERS_PH if peers[t]['d_sobre_v'] is not None)
KD, TAX = 5.1, 17.5
KE = RF + B_BL * ERP; WACC = (1 - DV) * KE + DV * KD * (1 - TAX / 100)
pharma_tasa = dict(
    regla='PFE y ABBV usan EXACTAMENTE esta tasa en el SOTP + rNPV (Base). La WACC propia de cada una se muestra solo como referencia / sensibilidad.',
    rf_pct=RF, erp_pct=ERP, beta_media_cruda_pares=round(B_RAW, 4), beta_blume=round(B_BL, 4), ke_pct=round(KE, 4),
    kd_pre_impuestos_pct=KD, tasa_impositiva_pct=TAX, kd_pct=round(KD * (1 - TAX / 100), 4), d_sobre_v_mediana_pares=round(DV, 4),
    wacc_pct=round(WACC, 3), wacc_bear_pct=round(WACC + 0.75, 3), wacc_bull_pct=round(WACC - 0.75, 3),
    grilla_sensibilidad_pct=[round(WACC + d, 3) for d in (-1, -0.5, 0, 0.5, 1)],
    construccion='CAPM: rf ^TNX 20-nov + beta Blume (0.67 x media cruda de 5 años de los 13 pares + 0.33) x ERP 5%; Kd 5.1% y tasa 17.5% como JNJ 3T26; D/V = mediana de los 13 pares (deuda total / (deuda + mcap al 20-nov)). Bear/Bull ±75 pb como JNJ.',
    pares_usados=PEERS_PH)

pes = [peers[t]['pe_fwd'] for t in PEERS_PH]
comparables_pharma = dict(
    regla='Mismo set de 13 pares para PFE y ABBV (sin PFE ni ABBV: anti-circularidad). Cada uno muestra al otro solo como referencia cruzada fuera del set. Múltiplo principal: P/E forward; correr la regresión P/E vs crecimiento antes de cualquier ajuste (skill informe-salud).',
    pares=peers,
    referencia_cruzada={t: dict(cierre_20nov=T[t]['cierre_20nov'], **T[t]['multiplos'],
                                eps_fy26=T[t]['consenso']['eps_ajustado_fy_actual'], eps_fy27=T[t]['consenso']['eps_ajustado_fy_siguiente'])
                        for t in ('PFE', 'ABBV')},
    estadisticos=dict(pe_fwd_mediana=round(float(np.median(pes)), 3), pe_fwd_q3=round(float(np.percentile(pes, 75)), 3),
                      pe_fwd_min=min(pes), pe_fwd_max=max(pes)),
    fuente=F_SA + '; cierres: ' + F_YH)

exito_clinico = dict(
    fuente='BIO / Informa Pharma Intelligence / QLS Advisors, Clinical Development Success Rates and Contributing Factors 2011-2020 (feb-2021), Figura 2 (pág. 7) y Figura 5b (pág. 11); 12,728 transiciones',
    url='https://go.bio.org/rs/490-EHZ-999/images/ClinicalDevelopmentSuccessRates2011_2020.pdf',
    regla='PFE y ABBV usan EXACTAMENTE estas probabilidades (por área terapéutica si el activo tiene área en la tabla; si no, "todas"). Ajustes solo con razón explícita y declarada, y el mismo ajuste en los dos informes si el caso es análogo.',
    columnas_transicion='Fase 1->2, Fase 2->3, Fase 3->presentación, presentación->aprobación (%)',
    transicion_por_fase={
        'todas': [52.0, 28.9, 57.8, 90.6], 'hematologia': [69.6, 48.1, 76.8, 93.1], 'metabolica': [61.8, 45.0, 63.6, 87.5],
        'infecciosas': [57.8, 38.4, 64.0, 92.9], 'oftalmologia': [71.6, 35.5, 51.2, 91.1], 'autoinmune': [55.2, 31.4, 65.3, 94.1],
        'alergia': [56.4, 28.3, 64.7, 100.0], 'gastroenterologia_no_eii': [46.7, 34.2, 57.1, 90.9], 'respiratoria': [55.9, 21.9, 64.5, 95.6],
        'psiquiatria': [52.7, 26.8, 56.3, 91.2], 'endocrina': [43.3, 26.6, 66.2, 86.3], 'neurologia': [47.7, 26.8, 53.1, 86.7],
        'oncologia': [48.8, 24.6, 47.7, 92.0], 'cardiovascular': [50.0, 21.0, 55.2, 82.5], 'urologia': [40.9, 15.0, 69.2, 84.6],
        'otras': [63.6, 38.6, 60.0, 88.4]},
    columnas_acumulada='Probabilidad de aprobación desde Fase 1, Fase 2, Fase 3, presentación (%)',
    probabilidad_acumulada_hasta_aprobacion={
        'todas': [7.9, 15.1, 52.4, 90.6], 'hematologia': [23.9, 34.4, 71.5, 93.1], 'metabolica': [15.5, 25.0, 55.7, 87.5],
        'infecciosas': [13.2, 22.8, 59.4, 92.9], 'oftalmologia': [11.9, 16.6, 46.7, 91.1], 'autoinmune': [10.7, 19.3, 61.4, 94.1],
        'alergia': [10.3, 18.3, 64.7, 100.0], 'gastroenterologia_no_eii': [8.3, 17.8, 51.9, 90.9], 'respiratoria': [7.5, 13.5, 61.6, 95.6],
        'psiquiatria': [7.3, 13.8, 51.4, 91.2], 'endocrina': [6.6, 15.2, 57.1, 86.3], 'neurologia': [5.9, 12.3, 46.0, 86.7],
        'oncologia': [5.3, 10.8, 43.9, 92.0], 'cardiovascular': [4.8, 9.6, 45.6, 82.5], 'urologia': [3.6, 8.8, 58.6, 84.6],
        'otras': [13.0, 20.5, 53.0, 88.4]},
    notas=['La Fig. 5b (LOA) usa n propios por fase y no es exactamente el producto de la Fig. 2: usar la Fig. 5b para la probabilidad acumulada.',
           'Vacunas no tienen fila propia: usar "infecciosas" (vacunas de PFE) y declararlo.',
           'Obesidad / diabetes (Metsera, PFE) = "metabolica". Inmunología (nuevas indicaciones de Skyrizi / Rinvoq) = "autoinmune". Migraña / Parkinson = "neurologia". Esquizofrenia / depresión = "psiquiatria". Oncología y ADC (Seagen, Elahere, Emrelis) = "oncologia".',
           'Extensión de indicación de un producto ya aprobado: la skill permite subir la probabilidad con razón explícita (mecanismo validado); declararlo y aplicar el mismo criterio en PFE y ABBV.'])

ira = dict(
    fuente_2026='CMS, fact sheet "Negotiated Prices for Initial Price Applicability Year 2026"; precio de lista de 30 días de 2023',
    fuente_2027='CMS, fact sheet "Negotiated Prices for Initial Price Applicability Year 2027"; precio de lista de 30 días de 2024',
    fuente_2028='CMS, fact sheet "Selected Drugs for Initial Price Applicability Year 2028" (27-ene-2026); gasto Medicare B+D nov-2024 a oct-2025',
    url='https://www.cms.gov/initiatives/medicare-prescription-drug-affordability/overview/medicare-drug-price-negotiation-program/selected-drugs-negotiated-prices',
    precios_2028='Los precios de la ronda 2028 se publican a más tardar el 30-nov-2026: NO estaban publicados al corte del 20-nov-2026. Modelar con un supuesto declarado (descuentos sobre lista de rondas previas: 2026 38%-79%, 2027 38%-85%).',
    farmacos=[
        dict(farmaco='Eliquis', compania='PFE (alianza con BMS, que figura como fabricante ante CMS)', ronda=2026, vigencia='2026-01-01',
             precio_lista_30d=521.00, precio_negociado_30d=231.00, descuento_pct=56, gasto_medicare_usd=18275108000, usuarios=3928000),
        dict(farmaco='Imbruvica', compania='ABBV (Pharmacyclics; J&J comparte fuera de EE.UU.)', ronda=2026, vigencia='2026-01-01',
             precio_lista_30d=14934.00, precio_negociado_30d=9319.00, descuento_pct=38, gasto_medicare_usd=2371858000, usuarios=17000),
        dict(farmaco='Ibrance', compania='PFE', ronda=2027, vigencia='2027-01-01',
             precio_lista_30d=15741, precio_negociado_30d=7871, descuento_pct=50, gasto_medicare_usd=2036178000, usuarios=16000),
        dict(farmaco='Xtandi', compania='PFE (Astellas figura como fabricante; PFE comparte el resultado en EE.UU.)', ronda=2027, vigencia='2027-01-01',
             precio_lista_30d=13480, precio_negociado_30d=7004, descuento_pct=48, gasto_medicare_usd=3401099000, usuarios=35000),
        dict(farmaco='Linzess', compania='ABBV (con Ironwood)', ronda=2027, vigencia='2027-01-01',
             precio_lista_30d=539, precio_negociado_30d=136, descuento_pct=75, gasto_medicare_usd=1982587000),
        dict(farmaco='Vraylar', compania='ABBV', ronda=2027, vigencia='2027-01-01',
             precio_lista_30d=1376, precio_negociado_30d=770, descuento_pct=44, gasto_medicare_usd=1136814000),
        dict(farmaco='Botox; Botox Cosmetic', compania='ABBV', ronda=2028, vigencia='2028-01-01', precio_negociado_30d=None, descuento_pct=None,
             gasto_medicare_usd=1143070000, usuarios=390000,
             nota='Parte B (primera ronda con Parte B). CMS aclara que el nombre "Cosmetic" no cambia la cobertura: el uso estético no lo paga Medicare.'),
        dict(farmaco='Xeljanz; Xeljanz XR', compania='PFE', ronda=2028, vigencia='2028-01-01', precio_negociado_30d=None, descuento_pct=None,
             gasto_medicare_usd=1013332000, usuarios=22000),
    ],
    nota_mfp='Descuento = (lista - negociado) / lista, sobre precio de LISTA; el efecto sobre el precio NETO es menor (ya había rebates). Estimar el impacto neto con lo que diga la compañía (10-K / 10-Q / call) y declararlo.',
    reglas_elegibilidad='Molécula pequeña: elegible a 7 años de la aprobación (precio efectivo a los 9); biológico: 11 (efectivo a los 13). Exclusión de huérfanos ampliada por la P.L. 119-21, según la fact sheet 2028.')

politica = dict(
    mfn_trumprx=dict(
        PFE=dict(fecha='2025-09-30',
                 terminos=['Precios MFN (igual al menor de países pares) en Medicaid desde 2026',
                           'Precio MFN garantizado en lanzamientos nuevos (Medicare, Medicaid y comercial)',
                           'Venta directa con descuento vía TrumpRx (descuentos promedio ~50%, hasta 85% sobre lista)',
                           'Inversión de US$70 mil millones en I+D y manufactura en EE.UU.',
                           'Período de gracia de 3 años sin aranceles de la Sección 232, condicionado a invertir'],
                 fuentes=['https://www.cnbc.com/2025/09/30/trump-pfizer-drug-price-agreement.html',
                          'https://www.fiercepharma.com/pharma/pfizer-plans-offer-price-concessions-trumps-most-favored-nation-push-reports']),
        ABBV=dict(fecha='2026-01-12',
                  terminos=['Precios MFN en Medicaid (ej. Synthroid, Combigan)', 'Venta directa vía TrumpRx (en vivo desde feb-2026)',
                            'Inversión de US$100 mil millones en 10 años (I+D y capital en EE.UU.)',
                            'Exención de 3 años del arancel de 100% a fármacos de marca, condicionada a ampliar la manufactura local'],
                  fuentes=['https://www.cnn.com/2026/01/12/politics/drug-prices-abbvie-trump',
                           'https://www.fiercepharma.com/pharma/abbvie-inks-latest-white-house-drug-pricing-deal-scoring-tariff-reprieve-it-makes-100b-us']),
        verificar='Términos de prensa. Cada informe confirma en el 10-Q del 3T26 (Risk Factors / MD&A) qué dice la compañía y cuantifica el impacto si lo da.'),
    aranceles_seccion_232=dict(
        proclama='Proclama 11020, 2-abr-2026, "Adjusting Imports of Pharmaceuticals and Pharmaceutical Ingredients into the United States"',
        tasas={'general_patentados': '100% (9903.04.60)', 'UE_Japon_Corea_Suiza': 'hasta 15% (9903.04.62)',
               'Reino_Unido': '0% según guía de CBP del 1-ago-2026 (Troutman, abr-2026, decía 10%)',
               'solo_plan_de_relocalizacion': '20% (9903.04.64), sube a 100% el 2-abr-2030',
               'relocalizacion_mas_acuerdo_MFN': '0% hasta el 20-ene-2029 (9903.04.65)',
               'especialidades': '0% huérfanos, terapias celulares / génicas, ADC, plasma, etc., con condiciones (9903.04.66)',
               'genericos_y_biosimilares': 'excluidos (revisión en un año)'},
        vigencia='31-jul-2026 para las 17 compañías del Anexo III (entre ellas Pfizer y AbbVie); 29-sep-2026 para el resto',
        estado_pfe_abbv='Ambas firmaron acuerdo MFN + plan de inversión, lo que las encuadraría en 0% (9903.04.65) hasta ene-2029. NO verificado contra el anexo oficial: confirmar en el 10-Q del 3T26 y declararlo.',
        fuentes=['https://www.troutman.com/insights/from-zero-to-100-new-section-232-tariffs-on-patented-drugs-and-the-high-stakes-onshoring-and-mfn-choices-ahead/ (7-abr-2026)',
                 'https://www.ghy.com/trade-compliance/us-imposes-100-section-232-tariffs-on-patented-pharmaceuticals-and-ingredients/ (actualizado 28-sep-2026)',
                 'https://www.mallorygroup.com/blog-posts/100-duties-two-deadlines-section-232-pharmaceutical-tariffs-take-effect-july-31-2026 (30-jul-2026)']))


def mj(p): return json.load(open(p, encoding='utf-8'))


LLY = mj('../../informe-salud/modelos/lly/model.json'); JNJ = mj('../../informe-salud/modelos/jnj/model.json')


def pub(m, t, extra):
    px = T[t]['cierre_20nov']
    return dict(fair_value_publicado=round(m['blend'], 2), precio_de_publicacion=m['price'], gap_publicado_pct=round(m['blend_gap'], 2),
                cierre_20nov=px, gap_al_20nov_pct=round((m['blend'] / px - 1) * 100, 2),
                pe_fy27_20nov=round(px / T[t]['consenso']['eps_ajustado_fy_siguiente'], 2), div_yield_20nov_pct=T[t]['multiplos']['div_yield_pct'],
                consenso_pt_20nov=T[t]['consenso']['pt_prom'], **extra)


ref_lly_jnj = dict(
    regla='Los fair values publicados NO se tocan: se muestran contra el precio con que se publicaron y se recalcula solo lo que depende del precio al 20-nov (regla PEP vs KO).',
    LLY=pub(LLY, 'LLY', dict(
        m1_sotp=round(LLY['m1'], 2), m2_comp=round(LLY['m2'], 2), m3_rev=round(LLY['m3'], 2), m4_cons=LLY['m4'], indep=round(LLY['indep'], 2),
        wacc_pct=round(LLY['wacc'], 3), rd_ventas_ttm_pct=round(LLY['ttm_rd_pct'], 2), margen_bruto_3t_pct=round(LLY['gm3'], 2),
        deuda_neta_usd_mm=round(LLY['net_debt'] * 1000), deuda_neta_ebitda=round(LLY['nd_lev'], 2),
        ventas_en_riesgo_loe_ttm_pct=round(LLY['loe_ttm_share'], 2))),
    JNJ=pub(JNJ, 'JNJ', dict(
        m1_sotp=round(JNJ['m1'], 2), m2_comp=round(JNJ['m2'], 2), m3_rev=round(JNJ['m3'], 2), m4_cons=JNJ['m4'],
        wacc_im_pct=round(JNJ['wacc_im'], 3), rd_ventas_ttm_pct=round(JNJ['ttm_rd_pct'], 2), margen_bruto_3t_pct=round(JNJ['gm3'], 2),
        deuda_neta_usd_mm=round(JNJ['net_debt'] * 1000), deuda_neta_ebitda=round(JNJ['nd_ebitda'], 2),
        ventas_en_riesgo_loe_pct=round(JNJ['loe_share'], 2), ventas_en_riesgo_loe_im_pct=round(JNJ['loe_share_im'], 2), anios_suba_dividendo=JNJ['div_years'])),
    fuente='.claude/skills/informe-salud/modelos/{lly,jnj}/model.json (3T26); precios y consenso al 20-nov: ' + F_SA,
    nota_wacc='LLY y JNJ se publicaron con rf 5.103% (13-nov). PFE / ABBV usan la rf del 20-nov: decirlo en el cuadro comparativo.')

WMT = mj('../../informe-consumo-masivo/modelos/wmt/model.json')
retail = dict(
    pares={t: dict(cierre_20nov=T[t]['cierre_20nov'], **T[t]['multiplos'],
                   eps_fy_actual=T[t]['consenso']['eps_ajustado_fy_actual'], eps_fy_siguiente=T[t]['consenso']['eps_ajustado_fy_siguiente'],
                   fy_actual_cierra=T[t]['consenso']['fy_actual_cierra'], pt_prom=T[t]['consenso']['pt_prom'], d_sobre_v=T[t]['balance_sa']['d_sobre_v'])
           for t in ('WMT', 'BJ', 'TGT', 'DG', 'DLTR', 'KR', 'AMZN')},
    pares_modelo_wmt=dict(
        fuente='.claude/skills/informe-consumo-masivo/modelos/wmt/model.py líneas 464-486 (PEERS: trimestres de consenso q, comparables sin combustible del último trimestre, NTM por ntm_rule) y model.json["peers"]',
        comparables_ultimo_trimestre_pct=dict(COST=6.7, TGT=5.6, KR=0.2, BJ=4.1, DG=3.5, DLTR=3.7),
        nota_BJ='El consenso anual de BJ en stockanalysis no estaba actualizado tras su 3T: WMT usa f1 = nueve meses reales (4.20) + 4T de consenso (1.04). Mantener el criterio.',
        nota_TGT='Su año fiscal incluye devoluciones de aranceles IEEPA (2T y 3T): excluir de la regresión contra crecimiento del EPS (criterio WMT).',
        WMT_publicado=dict(fair_value=round(WMT['blend'], 2), precio=WMT['price'], gap_pct=round(WMT['blend_gap'], 2), wacc_pct=round(WMT['wacc'], 3))),
    consumidor_eeuu=dict(
        texto_fuente='.claude/skills/informe-consumo-masivo/modelos/wmt/wmt.tpl.html, párrafo "El consumidor de EE.UU. al cierre de este informe" (Sección 05, 21-nov-2026)',
        ventas_minoristas_oct=dict(mm_pct=0.2, ia_pct=6.8, grupo_control_mm_pct=0.6, fuente='Census, avance del 17-nov-2026'),
        michigan_nov_preliminar=dict(valor=51.0, previo_oct=48.0, expectativa_inflacion_1a_pct=4.3, fuente='Universidad de Michigan, lectura preliminar de noviembre 2026'),
        ipc_oct_mm_pct=0.4, nota_ipc='El BLS no publica la variación interanual de octubre por la falta de datos de octubre de 2025.',
        diesel_semana_16nov=dict(usd_galon=5.94, vs_anio_previo=2.07, fuente='EIA'),
        nrf_navidad=dict(crecimiento_pct=4.2, nota='mitad volumen, mitad precio', fuente='NRF'),
        aranceles_consumo='IEEPA: se devuelven desde abril-2026; recargo de 10% de la Sección 122 vencido el 24-jul-2026; siguen Secciones 232 y 301.',
        lectura_wmt='WMT gana participación en todos los niveles de ingreso, liderada por hogares de ingresos altos.',
        nota_nafta='Para COST: con el combustible caro, las ventas totales y las comparables CON nafta están infladas; usar siempre comparables sin nafta ni tipo de cambio.'),
    fuente_multiplos=F_SA)


def bloque(t):
    return dict(cierre_20nov=T[t]['cierre_20nov'], max_52s=T[t]['max_52s'], min_52s=T[t]['min_52s'], multiplos=T[t]['multiplos'],
                balance=T[t]['balance_sa'], serie_mensual=f'defensivos_nov26/yh/{t}.mo.json (15 años) y {t}.d.json (2 años)')


out = dict(
    _meta=dict(creado='2026-11-22', fecha_corte_mercado=CUT,
               para=['COST (informe-consumo-masivo, bloque retail)', 'PFE (informe-salud, módulo A)', 'ABBV (informe-salud, módulo A)'],
               scripts='defensivos_nov26/{fetch_mercado.py, fetch_sa.py, mercado.py, construir.py}; crudos en defensivos_nov26/yh y defensivos_nov26/sa',
               regla='Leer de acá; no volver a buscar estos datos. Si un informe necesita un dato que no está, buscarlo y declararlo como propio del informe.'),
    mercado=mercado, consenso_tres=consenso,
    pharma=dict(tasa_descuento_comun=pharma_tasa, comparables=comparables_pharma, exito_clinico=exito_clinico,
                ira_medicare=ira, politica_precios_y_aranceles=politica, lly_jnj_3t26=ref_lly_jnj),
    retail=retail, cost_precio=bloque('COST'), pfe_precio=bloque('PFE'), abbv_precio=bloque('ABBV'),
    todos_los_tickers=T)
json.dump(out, open('../defensivos_nov26.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

print('WACC pharma', pharma_tasa['wacc_pct'], 'beta', round(B_BL, 3), 'DV', round(DV, 3), 'Ke', round(KE, 3))
print('S&P fwd ajustado', mercado['sp500']['pe_fwd_ajustado_20nov'], mercado['sectores_pe_fwd'])
print('pharma P/E', comparables_pharma['estadisticos'])
for t in ('COST', 'PFE', 'ABBV'): print(t, T[t]['balance_sa'])
print('LLY', ref_lly_jnj['LLY']['fair_value_publicado'], ref_lly_jnj['LLY']['gap_al_20nov_pct'], 'JNJ', ref_lly_jnj['JNJ']['fair_value_publicado'], ref_lly_jnj['JNJ']['gap_al_20nov_pct'])
