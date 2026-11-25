"""Valuación de Vista Energy (VIST) — skill informe-argentina + método sectorial de informe-energia. Corte: 24-nov-2026.

Copia de modelos/ypf/valuacion.py: cambia SOLO el bloque DATOS (y este docstring). Macro, deck de crudo,
comparables, consenso y serie de riesgo país: ../_compartido (búsqueda única, no se repite).

Fuentes propias: 6-K del 28-oct-2026 (resultados 3T26 y estados financieros al 30-sep-2026; Vista reporta en
USD bajo NIIF, moneda funcional USD → sin NIC 29); 6-K 24-nov-2026 (recompras: 110.287.402 acciones Serie A en
circulación); reservas 1P dic-2025 (588,1 MMboe, 6-K feb-2026 / Oil & Gas Journal); Yahoo (precios 24-nov).
Las cifras del 3T26 excluyen el 16,3% minoritario de Bandurria Sur Participaciones (como las publica Vista).

Correr: python valuacion.py  → imprime todo y escribe salida.json (lo que usa el HTML).
"""
import sys, os, json, statistics
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(AQUI, "..", "_compartido"))
from _ar import *                            # noqa: E402,F401
import contexto_energia_2026_11 as E         # noqa: E402

# =============================== DATOS (propios de la empresa) ===============================
DATOS = dict(
    ticker="VIST",
    nombre="Vista Energy",
    precio_adr=49.61,              # USD, cierre 24-nov-2026 (NYSE)
    precio_local=29980.0,          # ARS, CEDEAR VIST cierre 24-nov-2026 (BYMA)
    ratio_adr=1,                   # 1 ADS = 1 acción Serie A
    ratio_local=3,                 # 3 CEDEAR = 1 ADS (Rankia / TradingView)
    acciones=110_287_402,          # Serie A en circulación al 24-nov-2026 (6-K de recompras), sin las 2.014.351 en tesorería
    deuda=3_642.3, caja=785.0,     # USD M, 30-sep-2026
    asociadas=89.0,                # VMOS 9,09% (61,8) + otras (27,1), a libros
    otros_pasivos=624.0,           # pagos diferidos a Petronas 300 (2029-2030) + contraprestación contingente Equinor 324
    minoritarios=194.8,            # 16,3% de Bandurria Sur Participaciones (a libros)
    # ---- costo de capital
    lam=0.65,                      # λ: 72% de ingresos netos de exportación y 100% del crudo a paridad de exportación,
                                   #    reporta en USD, domicilio en México; piso 0,5 porque el 100% de los activos está en Argentina
    kd_spread_ratio=0.65,          # spread de sus ON / EMBI: ON XXXI 7,88% (abr-26, UST 4,28%, RP 527 → 0,68) y
                                   #    ON XXIX 8,50% (jun-25, UST 4,47%, RP 655 → 0,62); promedio 0,65
    # ---- operación (3T26, 6-K 28-oct-2026)
    brent_3t26=91.3, realizado_3t26=84.2,         # USD/bbl → descuento realizado 7,1
    petroleo_3t26=147.1,                          # kbbl/d
    gas_ngl_kboed=21.9,                           # gas 3,43 Mm3/d + LGN (169,0 − 147,1)
    upstream_ebitda_3t26=841.5,                   # USD M (EBITDA ajustado total: Vista es 100% upstream)
    take=0.197,                                   # (regalías 193,5 + derechos de exportación 50,2) / ingresos 1.234,1
    costo_caja_3t26=12.1,                         # USD/bbl de petróleo: (lifting 73,4 + venta 55,9 + G&A en efectivo 33,1) / 13,39 MMbbl
    costo_caja_boe=[12.1, 12.1, 12.1, 12.1, 12.1],
    da_boe=18.2,                                  # DD&A 283,6 / 15,55 MMboe (3T26)
    # producción de petróleo (kbbl/d) 2027-2031: guía 2027 185 kboe/d (87% petróleo ≈ 161), visión >200 kboe/d
    # a fin de la década; VMOS 50 kbbl/d firmes + Duplicar Norte (mar-2027)
    petroleo=dict(bear=[150, 153, 157, 161, 165], base=[161, 174, 187, 196, 200], bull=[165, 183, 200, 213, 222]),
    # descuento realizado vs. Brent: Base = 3T26; Bear = controles a la exportación/precio interno (ancla:
    # Medanito con descuentos de hasta 8,5 USD según Argus + derechos de exportación); Bull = VMOS (salida atlántica)
    descuento=dict(bear=12.0, base=7.1, bull=5.0),
    procesado_kbd=0.0, margen_rm=dict(bear=0.0, base=0.0, bull=0.0),   # sin refinación
    midstream_otros=0.0,
    otros_ebitda=0.0,                             # G&A ya está en el costo por barril
    capex=dict(bear=[1400] * 5, base=[1900, 1900, 1800, 1700, 1600], bull=[2100, 2200, 2100, 2000, 1900]),
    capex_mant_boe=13.0,                          # mismo supuesto que YPF (desarrollo 8,6 + brecha vs. Permian)
    capex_mant_fijo=50.0,
    # ---- reservas: 1P dic-2025 588,1 MMboe (PD 232,5 / PUD 355,7) + Bandurria Sur 25,1% y Bajo del Toro 35%
    # estimadas (26,0 kboe/d × 365 × 14,0 años de vida de reservas de Vista = 132,9) → 721 MMboe; 87% líquidos
    netback_gas_boe=8.1,                          # gas 3,3 USD/MMBtu × 6 = 19,8 USD/boe × (1 − 0,197) − 7,8 de costo ≈ 8,1
    res_liq=627.0, res_gas_ngl=94.0, prod_liq_año=53.7, prod_gas_año=8.0,
    capex_dev_boe=5.2,                            # 8,6 USD/boe × 60% (PUD / 1P de Vista)
    inventario_x_1p=1.0, riesgo_inventario=0.25, timing_inventario=0.6,
    # ---- serie propia para el Método 4: EV/EBITDA TTM (Vista reporta en USD: la serie de stockanalysis es limpia)
    ev_ebitda_trim=[2.24, 2.63, 1.98, 1.91, 2.40, 2.81, 3.50, 4.61, 4.16, 5.28, 5.07, 4.23, 5.71, 4.77, 5.06, 4.48,
                    4.99, 6.06, 4.81, 4.12],
    ebitda_trim={"3T25": 472.4, "2T26": 805.2, "3T26": 841.5},   # USD M ajustado (6-K)
    par_directo="YPF",
)
# =========================================================================================

D = DATOS
G = 0.02                                                 # crecimiento terminal en USD (piso del rango 2-3%)
adrs = D["acciones"] / D["ratio_adr"]
deuda_neta = D["deuda"] - D["caja"]
cap = D["precio_adr"] * adrs / 1e6
ccl_imp = ccl_implicito(D["precio_local"], D["ratio_local"], D["precio_adr"])
beta = beta_reapalancada(E.BETA_U_EYP, D["deuda"], cap, E.TASA_IMP)
w_d = D["deuda"] / (D["deuda"] + cap)
ajuste_puente = D["asociadas"] - deuda_neta - D["otros_pasivos"] - D["minoritarios"]

# Calibración del bloque de gas/LGN (residuo del EBITDA upstream del 3T26)
_vol_q = D["petroleo_3t26"] * 92 / 1000
_margen_q = D["realizado_3t26"] * (1 - D["take"]) - D["costo_caja_3t26"]
G_GAS_AÑO = (D["upstream_ebitda_3t26"] - _vol_q * _margen_q) * 4
PROD_3T26 = D["petroleo_3t26"] + D["gas_ngl_kboed"]


def ke(rp):
    return ke_usd(E.RF, beta, E.ERP, rp, D["lam"])


def wacc_rp(rp):
    return wacc(ke(rp), E.RF + D["kd_spread_ratio"] * rp / 10000, D["deuda"], cap, E.TASA_IMP)


def ebitda_año(oil_kbd, brent, macro, t):
    pr = brent - D["descuento"][macro]
    boe = oil_kbd + D["gas_ngl_kboed"]
    up = oil_kbd * 365 / 1000 * (pr * (1 - D["take"]) - D["costo_caja_boe"][t]) + G_GAS_AÑO * boe / PROD_3T26
    down = D["procesado_kbd"] * 365 / 1000 * D["margen_rm"][macro] + D["midstream_otros"]
    return up + down + D["otros_ebitda"], boe


def dcf(macro, crudo, rp1=None, rp_lp=None, brent_lp=None, detalle=False):
    esc = E.ESCENARIOS[macro]
    rp1 = esc["rp1"] if rp1 is None else rp1
    rp_lp = esc["rp_lp"] if rp_lp is None else rp_lp
    brent = E.brent_senda(E.DECK[crudo] if brent_lp is None else brent_lp)
    rps = crp_path(rp1, rp_lp)
    fcf, filas = [], []
    for t in range(5):
        eb, boe = ebitda_año(D["petroleo"][macro][t], brent[t], macro, t)
        da = D["da_boe"] * boe * 365 / 1000
        f = eb - E.TASA_IMP * max(0.0, eb - da) - D["capex"][macro][t]
        fcf.append(f)
        filas.append(dict(año=2027 + t, brent=brent[t], ebitda=eb, fcf=f, rp=rps[t], wacc=wacc_rp(rps[t])))
    # año terminal: producción del año 5, capex de mantenimiento = D&A (estado estable), crece G
    eb_t, boe_t = ebitda_año(D["petroleo"][macro][4], brent[4], macro, 4)
    capm = D["capex_mant_boe"] * boe_t * 365 / 1000 + D["capex_mant_fijo"]
    fcf_t = eb_t - E.TASA_IMP * max(0.0, eb_t - capm) - capm
    tasas = [wacc_rp(r) for r in rps]
    factor, pv = 1.0, 0.0
    for f, r in zip(fcf, tasas):
        factor *= 1 + r
        pv += f / factor
    tv = fcf_t * (1 + G) / (wacc_rp(rp_lp) - G) / factor
    ev = pv + tv
    por_adr = (ev + ajuste_puente) / adrs * 1e6
    if detalle:
        return dict(por_adr=por_adr, ev=ev, pct_terminal=tv / ev, filas=filas, fcf_terminal=fcf_t, capex_mant=capm)
    return por_adr


def sotp(macro, crudo, rp_lp=None, brent_lp=None):
    """Método sectorial (informe-energia, integrada): NAV upstream 1P + inventario arriesgado + refinación a
    múltiplo de refinadoras ajustado por país + asociadas − deuda neta − corporativo a perpetuidad."""
    rp_lp = E.ESCENARIOS[macro]["rp_lp"] if rp_lp is None else rp_lp
    r = wacc_rp(rp_lp)
    brent = E.DECK[crudo] if brent_lp is None else brent_lp
    nb_liq = (brent - D["descuento"][macro]) * (1 - D["take"]) - D["costo_caja_boe"][-1]
    nav_liq = E.nav_reservas(D["res_liq"], D["prod_liq_año"], nb_liq, r, D["capex_dev_boe"])
    nb_gas = G_GAS_AÑO / D["prod_gas_año"] if D["netback_gas_boe"] is None else D["netback_gas_boe"]
    nav_gas = E.nav_reservas(D["res_gas_ngl"], D["prod_gas_año"], nb_gas, r)
    nav_inv = (nav_liq / D["res_liq"]) * D["res_liq"] * D["inventario_x_1p"] * D["riesgo_inventario"] * D["timing_inventario"]
    mult_ref = statistics.median(E.REFINADORAS.values())
    m_ar = multiplo_ajustado_por_pais(mult_ref, ke(0), ke(rp_lp), G)
    ebitda_ref = D["procesado_kbd"] * 365 / 1000 * D["margen_rm"][macro] + D["midstream_otros"]
    corp = D["otros_ebitda"] * (1 - E.TASA_IMP) / (r - G)
    total = nav_liq + nav_gas + nav_inv + ebitda_ref * m_ar + corp
    partes = dict(nav_liquidos=nav_liq, nav_gas=nav_gas, inventario=nav_inv, refinacion=ebitda_ref * m_ar,
                  corporativo=corp, mult_ref_ar=m_ar)
    return (total + ajuste_puente) / adrs * 1e6, partes


def ebitda_mid():
    """EBITDA de mitad de ciclo: año 2027 con macro Base y Brent Base (70) en todo el año."""
    return ebitda_año(D["petroleo"]["base"][0], E.DECK["base"], "base", 0)[0]


def comps(rp_lp, ebitda_ref=None):
    eb = ebitda_mid() if ebitda_ref is None else ebitda_ref
    filas = {}
    for n, (ev_e, pe, evb, dn, dy, pais, grupo) in E.COMPS.items():
        if pais == "AR":
            continue
        ke_p = E.RF + beta * E.ERP + E.CRP_PAIS[pais]
        filas[n] = multiplo_ajustado_por_pais(ev_e, ke_p, ke(rp_lp), G)
    ms = sorted(filas.values())
    med = statistics.median(ms)
    q = statistics.quantiles(ms, n=4)
    f = lambda m: (m * eb + ajuste_puente) / adrs * 1e6
    return f(med), filas, (f(q[0]), f(q[2])), med


def serie_multiplos():
    if D.get("ev_ebitda_trim"):
        return list(E.RP_TRIM), list(D["ev_ebitda_trim"]), list(E.TRIM)
    xs, ys, fechas = [], [], []
    for i, f in enumerate(E.TRIM):
        dn, nlr = D["deuda_neta_trim"][i], D["nlr_trim"][i]
        if dn is None:   # 1T23 y 2T23: interpolación lineal entre 4T22 y 3T23 (los 6-K no publican el monto)
            a, b = D["deuda_neta_trim"][4], D["deuda_neta_trim"][7]
            dn = a + (b - a) * (i - 4) / 3
        ebitda_ltm = dn / nlr
        ev = D["adr_trim"][i] * adrs / 1e6 + dn
        xs.append(E.RP_TRIM[i]); ys.append(ev / ebitda_ltm); fechas.append(f)
    return xs, ys, fechas


def reversion(rp_eval, ebitda_ref=None):
    xs, ys, fechas = serie_multiplos()
    a, b, r2 = E.regresion_rp(xs, ys)
    m = a + b * rp_eval
    eb = ebitda_mid() if ebitda_ref is None else ebitda_ref
    return (m * eb + ajuste_puente) / adrs * 1e6, dict(a=a, b=b, r2=r2, n=len(xs), mult=m,
                                                         regimen=E.regimenes(xs, ys), puntos=list(zip(xs, ys, fechas)))


def consenso():
    v = [x[2] for x in E.CONSENSO[D["ticker"]]]
    return statistics.mean(v), min(v), max(v)


def valuar(rp_lp_base=None, brent_base=None, detalle=False):
    rp_lp_base = E.ESCENARIOS["base"]["rp_lp"] if rp_lp_base is None else rp_lp_base

    def combo(fn):
        def f(m, c):
            kw = {}
            if m == "base":
                kw["rp_lp"] = rp_lp_base
            if c == "base" and brent_base is not None:
                kw["brent_lp"] = brent_base
            out = fn(m, c, **kw)
            return out[0] if isinstance(out, tuple) else out
        return f

    t_dcf, v_dcf = E.matriz_9(combo(dcf))
    t_sec, v_sec = E.matriz_9(combo(sotp))
    eb_ref = None
    if brent_base is not None:
        eb_ref = ebitda_año(D["petroleo"]["base"][0], brent_base, "base", 0)[0]
    v_cmp, filas, rango_cmp, med_cmp = comps(rp_lp_base, eb_ref)
    v_rev, reg = reversion(rp_lp_base, eb_ref)
    v_con, cmin, cmax = consenso()
    vals = {"dcf": v_dcf, "sectorial": v_sec, "comps": v_cmp, "reversion": v_rev, "consenso": v_con}
    fv = blend(vals)
    if not detalle:
        return fv
    return dict(fv=fv, vals=vals, t_dcf=t_dcf, t_sec=t_sec, comps=(filas, rango_cmp, med_cmp), rev=reg,
                con=(cmin, cmax))


def rp_implicito():
    """Riesgo país CONSTANTE (año 1 = largo plazo) que iguala el DCF Base (macro y crudo Base) al precio."""
    return riesgo_pais_implicito(D["precio_adr"], lambda c: dcf("base", "base", rp1=c, rp_lp=c), lo=0, hi=6000)


def brent_implicito():
    """Brent de largo plazo que iguala el DCF Base (riesgo país del Base) al precio."""
    lo, hi = 20.0, 150.0
    f = lambda b: dcf("base", "base", brent_lp=b)
    if not (f(lo) <= D["precio_adr"] <= f(hi)):
        return None
    while hi - lo > 0.01:
        mid = (lo + hi) / 2
        if f(mid) > D["precio_adr"]:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def breakeven_brent():
    """Brent que cubre impuestos + capex de mantenimiento + intereses (año 2027, macro Base)."""
    interes = D["deuda"] * 0.073                    # tasa promedio de la deuda en USD 3T26
    def caja(b):
        eb, boe = ebitda_año(D["petroleo"]["base"][0], b, "base", 0)
        capm = D["capex_mant_boe"] * boe * 365 / 1000 + D["capex_mant_fijo"]
        return eb - E.TASA_IMP * max(0, eb - capm) - capm - interes
    lo, hi = 0.0, 150.0
    while hi - lo > 0.01:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if caja(mid) < 0 else (lo, mid)
    return (lo + hi) / 2


if __name__ == "__main__":
    r = valuar(detalle=True)
    fv = r["fv"]
    rpi, bri, bke = rp_implicito(), brent_implicito(), breakeven_brent()
    esc = E.ESCENARIOS
    print(f"=== {D['nombre']} ({D['ticker']}) — corte {E.FECHA_CORTE} ===")
    print(f"ADR USD {D['precio_adr']:.2f} | local ARS {D['precio_local']:,.1f} | CCL implícito {ccl_imp:,.1f} "
          f"| brecha vs mayorista {brecha(ccl_imp, E.OFICIAL_MAYORISTA):.1%}")
    print(f"ADRs equivalentes {adrs / 1e6:.1f} M | capitalización USD {cap:,.0f} M | deuda neta {deuda_neta:,.0f} | "
          f"EV {cap + deuda_neta:,.0f}")
    print(f"beta reapalancada {beta:.2f} (D/E {D['deuda'] / cap:.2f}) | D/V {w_d:.0%} | λ {D['lam']} | "
          f"gas+LGN calibrado USD {G_GAS_AÑO:,.0f} M/año")
    for k in ("bear", "base", "bull"):
        p = crp_path(esc[k]["rp1"], esc[k]["rp_lp"])
        print(f"  {k:4} RP {esc[k]['rp1']:.0f}→{esc[k]['rp_lp']:.0f} | Ke {ke(p[0]):.2%}→{ke(p[-1]):.2%} | "
              f"WACC {wacc_rp(p[0]):.2%}→{wacc_rp(p[-1]):.2%} | p={esc[k]['p']:.0%}")
    print(f"  Ke con CRP Damodaran 9,71% y λ: {ke(971):.2%}")
    d0 = dcf("base", "base", detalle=True)
    print("\nM1 DCF Base/Base por año:")
    for f in d0["filas"]:
        print(f"  {f['año']} Brent {f['brent']:5.1f} | EBITDA {f['ebitda']:7,.0f} | FCF {f['fcf']:7,.0f} | "
              f"RP {f['rp']:5.0f} | WACC {f['wacc']:.2%}")
    print(f"  terminal FCF {d0['fcf_terminal']:,.0f} (capex mant. {d0['capex_mant']:,.0f}) | % EV desde terminal "
          f"{d0['pct_terminal']:.0%} | por ADR {d0['por_adr']:.2f}")
    print("Matriz 9 (DCF, USD/ADR) filas macro, columnas crudo bear/base/bull:")
    for m in ("bear", "base", "bull"):
        print(f"  {m:4} " + " ".join(f"{r['t_dcf'][(m, c)]:7.2f}" for c in ("bear", "base", "bull")))
    print(f"  esperado {r['vals']['dcf']:.2f}")
    print("M2 SOTP (USD/ADR):")
    for m in ("bear", "base", "bull"):
        print(f"  {m:4} " + " ".join(f"{r['t_sec'][(m, c)]:7.2f}" for c in ("bear", "base", "bull")))
    _, partes = sotp("base", "base")
    print("  partes Base/Base (USD M):", {k: round(v, 2) for k, v in partes.items()}, "| esperado", round(r["vals"]["sectorial"], 2))
    filas, rango, med = r["comps"]
    print(f"M3 comparables ajustados (mediana {med:.2f}x sobre EBITDA mid-cycle {ebitda_mid():,.0f}) → "
          f"{r['vals']['comps']:.2f} (P25-P75 {rango[0]:.2f}-{rango[1]:.2f})")
    for n, m in filas.items():
        print(f"  {n:18} {E.COMPS[n][0]:.2f}x → {m:.2f}x")
    rv = r["rev"]
    print(f"M4 reversión EV/EBITDA = {rv['a']:.2f} {rv['b'] * 1000:+.3f}×(RP/1000) | R² {rv['r2']:.2f} | n {rv['n']} | "
          f"en {esc['base']['rp_lp']:.0f} pb → {rv['mult']:.2f}x → {r['vals']['reversion']:.2f}")
    print("  regímenes:", {k: (round(v[0], 2), v[1]) for k, v in rv["regimen"].items()})
    print(f"M5 consenso {r['vals']['consenso']:.2f} (rango {r['con'][0]:.2f}-{r['con'][1]:.2f}, n={len(E.CONSENSO[D['ticker']])})")
    print(f"\nBLEND (15/15/20/30/20) = USD {fv:.2f} por ADR vs precio {D['precio_adr']:.2f} → {fv / D['precio_adr'] - 1:+.1%}")
    print(f"M6 riesgo país implícito (constante) = {rpi:.0f} pb vs mercado {E.RP_SPOT} pb (prom. 90 d {E.RP_PROM_90D})")
    print(f"Brent implícito (LP, RP del Base) = USD {bri:.1f}" if bri else "Brent implícito: fuera de rango")
    print(f"Breakeven (impuestos + capex mant. + intereses, 2027): Brent USD {bke:.1f}")
    eb27 = d0["filas"][0]["ebitda"]
    print(f"EV/EBITDA 2027 Base: {(cap + deuda_neta) / eb27:.2f}x | FCF yield 2027 Base {d0['filas'][0]['fcf'] / cap:.1%} | "
          f"EBITDA mid-cycle {ebitda_mid():,.0f}")

    rps = [550, 680, esc["base"]["rp_lp"], 950, 1100]
    brs = [60.0, 65.0, 70.0, 75.0, 80.0]
    grilla = [[valuar(rp, b) for b in brs] for rp in rps]
    assert abs(grilla[2][2] - fv) < 1e-6, "la celda Base tiene que ser el fair value publicado"
    print("\nGrilla (filas RP LP pb; columnas Brent LP):", brs)
    for rp, fila in zip(rps, grilla):
        print(f"  {rp:7.1f} " + " ".join(f"{v:7.2f}" for v in fila))

    base = d0["por_adr"]
    print("\nCHEQUEO DE SESGO:")
    print(f"  DCF Base / precio = {base / D['precio_adr']:.2f} (alerta fuera de 0,5-1,5) | peor celda de la matriz "
          f"{min(r['t_dcf'].values()):.2f} (>0)")
    print("  1 monedas: todo en USD (moneda funcional USD, cifras del 6-K en USD); tasa en USD → OK")
    print("  2 riesgo país 1 vez: beta E&P EE.UU. reapalancada (no local) + λ×EMBI; el Bear macro recorta capex y crecimiento pero no lleva la producción a cero ni suma un CRP terminal de crisis → OK")
    print("  3 tipo de cambio: no aplica a flujos (USD); CCL solo para el precio local → OK")
    print("  4 año base: EBITDA mid-cycle a Brent 70, no el 3T26 a Brent 91 ni el 2T26 récord → OK")
    print("  5 limpio: EBITDA ajustado (sin ventas de activos, valor razonable de activos en venta, IFRS 16) → OK")

    xs, ys, fechas = serie_multiplos()
    ebitda_ltm = [] if D.get("ev_ebitda_trim") else [round((D['deuda_neta_trim'][i] or (D['deuda_neta_trim'][4] + (D['deuda_neta_trim'][7] - D['deuda_neta_trim'][4]) * (i - 4) / 3)) / D['nlr_trim'][i]) for i in range(len(E.TRIM))]
    reg = rv["regimen"]
    ff = {
        "dcf": (min(r["t_dcf"].values()), max(r["t_dcf"].values())),
        "sectorial": (min(r["t_sec"].values()), max(r["t_sec"].values())),
        "comps": rango,
        "reversion": tuple((min(v[0] for v in reg.values()) * ebitda_mid() + ajuste_puente) / adrs * 1e6 if j == 0 else
                           (max(v[0] for v in reg.values()) * ebitda_mid() + ajuste_puente) / adrs * 1e6 for j in (0, 1)),
        "consenso": r["con"],
    }
    print("Football field:", {k: (round(a, 2), round(b, 2)) for k, (a, b) in ff.items()})
    out = dict(
        fecha_corte=E.FECHA_CORTE, ticker=D["ticker"], precio_adr=D["precio_adr"], precio_local=D["precio_local"],
        ccl_implicito=ccl_imp, cap=cap, deuda_neta=deuda_neta, ev=cap + deuda_neta, beta=beta, fair_value=fv,
        upside=fv / D["precio_adr"] - 1, rp_implicito=rpi, brent_implicito=bri, breakeven=bke, metodos=r["vals"],
        matriz_dcf={f"{m}|{c}": v for (m, c), v in r["t_dcf"].items()},
        matriz_sotp={f"{m}|{c}": v for (m, c), v in r["t_sec"].items()}, sotp_partes=partes,
        dcf_base=dict(filas=d0["filas"], pct_terminal=d0["pct_terminal"], por_adr=d0["por_adr"]),
        comps={"por_par": filas, "p25": rango[0], "p75": rango[1], "mediana_x": med}, ebitda_mid=ebitda_mid(),
        reversion={k: v for k, v in rv.items()}, consenso_rango=r["con"],
        grilla={"rp": rps, "brent": brs, "valores": grilla}, football=ff, ebitda_ltm=list(zip(E.TRIM, ebitda_ltm)),
        ke={k: [ke(x) for x in crp_path(v["rp1"], v["rp_lp"])] for k, v in esc.items()},
        wacc={k: [wacc_rp(x) for x in crp_path(v["rp1"], v["rp_lp"])] for k, v in esc.items()},
        g_gas=G_GAS_AÑO,
    )
    json.dump(out, open(os.path.join(AQUI, "salida.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\nsalida.json escrito")
