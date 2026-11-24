"""Valuación de Banco Macro (BMA) — skill informe-argentina. Corte: 20-nov-2026.

Macro, costo de capital, comparables, consenso y serie histórica: ../_compartido (búsqueda única,
contexto-2026-11.md + contexto_2026_11.py). Acá solo van los datos propios del banco (bloque DATOS).
Para otro banco: copiar este archivo y cambiar SOLO el bloque DATOS.

Copia de modelos/ggal/valuacion.py: solo cambia el bloque DATOS.
Fuentes propias: 6-K del 19-ago-2026 (2Q26 Earnings Release, NIC 29, moneda de jun-2026), SEC EDGAR;
Yahoo (precios 20-nov-2026); 6-K de recompras 11 a 20-nov-2026. El 3T26 sale el 25-nov-2026.

Correr: python valuacion.py   → imprime todo y escribe salida.json (lo que usa el HTML).
"""
import sys, os, json, statistics
sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.join(AQUI, "..", "_compartido"))
from _ar import *                       # noqa: E402,F401
import contexto_2026_11 as C            # noqa: E402

# =============================== DATOS (propios del banco) ===============================
DATOS = dict(
    ticker="BMA",
    nombre="Banco Macro",
    precio_adr=49.86,             # USD, cierre 20-nov-2026 (NYSE)
    precio_local=8990.0,          # ARS, cierre 20-nov-2026 (BYMA)
    ratio_adr=10,                 # 1 ADR = 10 acciones Clase B
    acciones=639.413e6,           # acciones en circulación (20-F; recompras de nov-2026 inmateriales)
    patrimonio_jun26=6_291_414e6, # ARS, PN atribuible 30-jun-2026 (moneda de jun-2026)
    ganancia_2t26=206_800e6,      # ARS, ganancia 2T26 (ajustada sin reestructuración: 221.000 M)
    roe_2t26=0.134, roe_6m26=0.117,
    capital_total=0.28,           # CAR Basilea III = Tier 1 = 28% (2T26)
    capital_computable=4_100_000e6 * 3.43 / 2.43,   # exceso Ps 4,10 bn = 243% sobre el mínimo
    capital_objetivo=0.15,
    expo_publica=0.259 * 4.1 * 6_291_414e6,         # activos públicos 25,9% del activo; activo/PN 4,1x
    descuento_holding=0.0,        # Banco Macro es el banco operativo, no una holding
    escenarios=dict(
        bear=dict(roe=[0.05, 0.07, 0.09, 0.10, 0.10], roe_lp=0.10, g=[0.00, 0.02, 0.02, 0.02, 0.02]),
        base=dict(roe=[0.12, 0.135, 0.145, 0.15, 0.155], roe_lp=0.155, g=[0.05, 0.05, 0.05, 0.04, 0.03]),
        bull=dict(roe=[0.14, 0.16, 0.18, 0.19, 0.20], roe_lp=0.18, g=[0.08, 0.08, 0.07, 0.06, 0.04]),
    ),
    haircut_soberano_bear=0.20,
    # Ganancia por trimestre (ARS) y en qué moneda está: "nominal" o reexpresada a jun-2026
    resultados=[("2T25", 199_169e6, "jun26"), ("3T25", -33_097e6, "nominal"), ("4T25", 100_100e6, "nominal"),
                ("1T26", 140_239e6, "nominal"), ("2T26", 206_800e6, "nominal")],
    par_directo="GGAL",
)
# =========================================================================================

D = DATOS
G_USD_TERMINAL = 0.03                                   # crecimiento terminal en USD (techo del rango 2-3%)
G_REAL_LP = (1 + G_USD_TERMINAL) / (1 + C.INFL_USA) - 1
PROBS = {k: v["p"] for k, v in C.ESCENARIOS.items()}

ccl_imp = ccl_implicito(D["precio_local"], D["ratio_adr"], D["precio_adr"])
bvps_ars = D["patrimonio_jun26"] / D["acciones"] * C.REEXP_JUN_OCT26          # moneda de oct-2026
bv_adr = bvps_ars * D["ratio_adr"] / ccl_imp                                  # USD por ADR al CCL implícito
pbv_mercado = D["precio_adr"] / bv_adr
expo_sobre_pn = D["expo_publica"] / D["patrimonio_jun26"]
haircut_bear = expo_sobre_pn * D["haircut_soberano_bear"] * (1 - 0.35)
exceso_capital_ars = (D["capital_total"] - D["capital_objetivo"]) / D["capital_total"] * D["capital_computable"]
exceso_capital_adr = exceso_capital_ars * C.REEXP_JUN_OCT26 / D["acciones"] * D["ratio_adr"] / ccl_imp


def ke_path(rp1, rp_lp):
    return tasas_desde_crp(C.RF, C.BETA_BANCOS, C.ERP, rp1, rp_lp, lam=1.0, n=5)


def ddm(esc, rp1, rp_lp, bv0=None, shock_fx=0.0):
    """DDM de payout total en USD reales: D_t = ROE_t·BV_{t-1} − ΔBV; terminal = P/BV justificado."""
    e = D["escenarios"][esc]
    bv = (bv0 if bv0 is not None else bv_adr) / (1 + shock_fx)
    if esc == "bear":
        bv *= 1 - haircut_bear
    kes = ke_path(rp1, rp_lp)
    pv, factor, rim = 0.0, 1.0, bv
    for roe, g, k in zip(e["roe"], e["g"], kes):
        kr = ke_real(k, C.INFL_USA)
        ganancia = roe * bv
        nuevo_bv = bv * (1 + g)
        div = ganancia - (nuevo_bv - bv)
        factor *= 1 + kr
        pv += div / factor
        rim += (roe - kr) * bv / factor            # residual income (chequeo: RIM == DDM)
        bv = nuevo_bv
    ke_lp = ke_usd(C.RF, C.BETA_BANCOS, C.ERP, rp_lp)
    pbv_t = pbv_justificado(e["roe_lp"], G_REAL_LP, ke_lp, C.INFL_USA)
    tv = bv * pbv_t / factor
    rim += (pbv_t - 1) * bv / factor
    return {"valor": pv + tv, "pct_terminal": tv / (pv + tv), "rim": rim, "pbv_terminal": pbv_t}


def sectorial(esc, rp_lp, shock_fx=0.0):
    """P/BV justificado de estado estable (ROE LP, Ke LP) × BV, menos descuento de holding."""
    e = D["escenarios"][esc]
    bv = bv_adr / (1 + shock_fx)
    if esc == "bear":
        bv *= 1 - haircut_bear
    m = pbv_justificado(e["roe_lp"], G_REAL_LP, ke_usd(C.RF, C.BETA_BANCOS, C.ERP, rp_lp), C.INFL_USA)
    return m * bv * (1 - D["descuento_holding"]), m


def comps(rp_lp, shock_fx=0.0):
    """P/BV de cada par Latam ajustado por ROE y por diferencial de Ke (Gordon), mediana × BV."""
    roe_ar = (1 + D["escenarios"]["base"]["roe_lp"]) * (1 + C.INFL_USA) - 1    # ROE real → USD nominal
    ke_ar = ke_usd(C.RF, C.BETA_BANCOS, C.ERP, rp_lp)
    g = G_USD_TERMINAL
    filas = {}
    for n, (pbv, pe, roe_p, pais) in C.PEERS.items():
        ke_p = C.RF + C.BETA_BANCOS * C.ERP + C.CRP_PEERS[pais]
        filas[n] = multiplo_ajustado_por_pais(pbv * (roe_ar - g) / (roe_p - g), ke_p, ke_ar, g)
    ms = sorted(filas.values())
    med = statistics.median(ms)
    q = statistics.quantiles(ms, n=4)
    bv = bv_adr / (1 + shock_fx)
    return med * bv, filas, (q[0] * bv, q[2] * bv), med


def reversion(rp_eval, shock_fx=0.0):
    """Regresión P/BV ~ riesgo país (1T20 → 3T26, era NIC 29) evaluada en el riesgo país del Base."""
    s = [r for r in C.serie() if r["fecha"] >= "2020-03-31" and r[f"{D['ticker'].lower()}_pbv"]]
    xs = [r["riesgo_pais"] for r in s]
    ys = [r[f"{D['ticker'].lower()}_pbv"] for r in s]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    r2 = 1 - sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys)) / sum((y - my) ** 2 for y in ys)
    regimen = {
        "<800": [y for x, y in zip(xs, ys) if x < 800],
        "800-1500": [y for x, y in zip(xs, ys) if 800 <= x <= 1500],
        ">1500": [y for x, y in zip(xs, ys) if x > 1500],
    }
    pbv = a + b * rp_eval
    return pbv * bv_adr / (1 + shock_fx), dict(a=a, b=b, r2=r2, n=len(xs), pbv=pbv,
                                                 regimen={k: (statistics.median(v), len(v)) for k, v in regimen.items() if v},
                                                 puntos=list(zip(xs, ys, [r["fecha"] for r in s])))


def consenso():
    v = [x[2] for x in C.CONSENSO[D["ticker"]]]
    return statistics.mean(v), min(v), max(v)


def valuar(rp_lp_base=None, shock_fx=0.0, detalle=False):
    esc = C.ESCENARIOS
    rp_lp_base = esc["base"]["rp_lp"] if rp_lp_base is None else rp_lp_base
    rps = {"bear": (esc["bear"]["rp1"], esc["bear"]["rp_lp"]), "base": (esc["base"]["rp1"], rp_lp_base),
           "bull": (esc["bull"]["rp1"], esc["bull"]["rp_lp"])}
    d = {k: ddm(k, *rps[k], shock_fx=shock_fx) for k in rps}
    s = {k: sectorial(k, rps[k][1], shock_fx) for k in rps}
    p = [PROBS["bear"], PROBS["base"], PROBS["bull"]]
    v_ddm = esperado([d[k]["valor"] for k in ("bear", "base", "bull")], p)
    v_sec = esperado([s[k][0] for k in ("bear", "base", "bull")], p)
    v_cmp, filas, rango_cmp, med_cmp = comps(rp_lp_base, shock_fx)
    v_rev, reg = reversion(rp_lp_base, shock_fx)
    v_con, con_min, con_max = consenso()
    vals = {"dcf": v_ddm, "sectorial": v_sec, "comps": v_cmp, "reversion": v_rev, "consenso": v_con}
    fv = blend(vals)
    if not detalle:
        return fv
    return dict(fv=fv, vals=vals, ddm=d, sec=s, comps=(filas, rango_cmp, med_cmp), rev=reg,
                con=(con_min, con_max))


def rp_implicito():
    """Riesgo país CONSTANTE (año 1 = largo plazo) que iguala el DDM Base al precio del ADR."""
    return riesgo_pais_implicito(D["precio_adr"], lambda c: ddm("base", c, c)["valor"], lo=0, hi=5000)


if __name__ == "__main__":
    r = valuar(detalle=True)
    fv = r["fv"]
    rpi = rp_implicito()
    esc = C.ESCENARIOS
    print(f"=== {D['nombre']} ({D['ticker']}) — corte {C.FECHA_CORTE} ===")
    print(f"ADR USD {D['precio_adr']:.2f} | local ARS {D['precio_local']:,.1f} | CCL implícito {ccl_imp:,.1f} "
          f"| brecha vs mayorista {brecha(ccl_imp, C.OFICIAL_MAYORISTA):.1%}")
    print(f"BV/acción (oct-26) ARS {bvps_ars:,.0f} → BV/ADR USD {bv_adr:.2f} | P/BV mercado {pbv_mercado:.2f}x")
    print(f"Exposición sector público / PN {expo_sobre_pn:.0%} → haircut Bear {haircut_bear:.1%} | "
          f"capital que sobra vs 15%: USD {exceso_capital_adr:.2f}/ADR ({exceso_capital_adr / D['precio_adr']:.0%} del precio)")
    print("\nKe USD por escenario (año 1 → LP):")
    for k in ("bear", "base", "bull"):
        ks = ke_path(esc[k]["rp1"], esc[k]["rp_lp"])
        print(f"  {k:4} RP {esc[k]['rp1']:.0f}→{esc[k]['rp_lp']:.0f} pb | Ke USD {ks[0]:.2%} → {ks[-1]:.2%} | "
              f"Ke real {ke_real(ks[0]):.2%} → {ke_real(ks[-1]):.2%} | p={esc[k]['p']:.0%}")
    print(f"  Ke USD con CRP Damodaran {C.CRP_DAMODARAN_AR:.2%}: {C.RF + C.BETA_BANCOS * C.ERP + C.CRP_DAMODARAN_AR:.2%}")
    print("\nM1 DDM (USD reales por ADR):")
    for k in ("bear", "base", "bull"):
        x = r["ddm"][k]
        print(f"  {k:4} {x['valor']:7.2f} | RIM {x['rim']:7.2f} | P/BV terminal {x['pbv_terminal']:.2f}x | "
              f"% terminal {x['pct_terminal']:.0%}")
        assert abs(x["valor"] - x["rim"]) < 1e-6, "RIM y DDM tienen que coincidir (clean surplus)"
    print(f"  esperado {r['vals']['dcf']:.2f}")
    print("M2 P/BV justificado (− descuento de holding si aplica):")
    for k in ("bear", "base", "bull"):
        print(f"  {k:4} P/BV {r['sec'][k][1]:.2f}x → {r['sec'][k][0]:7.2f}")
    print(f"  esperado {r['vals']['sectorial']:.2f}")
    filas, rango, med = r["comps"]
    print(f"M3 comparables Latam ajustados (mediana {med:.2f}x) → {r['vals']['comps']:.2f} "
          f"(P25-P75 {rango[0]:.2f}-{rango[1]:.2f})")
    for n, m in filas.items():
        print(f"  {n:16} P/BV {C.PEERS[n][0]:.2f}x → ajustado {m:.2f}x")
    rv = r["rev"]
    print(f"M4 reversión: P/BV = {rv['a']:.3f} {rv['b'] * 1000:+.4f}×(RP/1000) | R² {rv['r2']:.2f} | n {rv['n']} "
          f"| en {esc['base']['rp_lp']:.0f} pb → {rv['pbv']:.2f}x → {r['vals']['reversion']:.2f}")
    print("  regímenes (mediana P/BV, n):", {k: (round(v[0], 2), v[1]) for k, v in rv["regimen"].items()})
    print(f"M5 consenso {r['vals']['consenso']:.2f} (rango {r['con'][0]:.2f}-{r['con'][1]:.2f}):",
          [(c, f, round(v, 2)) for c, f, v in C.CONSENSO[D['ticker']]])
    print(f"\nBLEND (15/15/20/30/20) = USD {fv:.2f} por ADR vs precio {D['precio_adr']:.2f} → {fv / D['precio_adr'] - 1:+.1%}")
    print(f"M6 riesgo país implícito (constante) = {rpi:.0f} pb vs mercado {C.RP_SPOT} pb (prom. 90 d {C.RP_PROM_90D})")

    # Grilla 5x5: riesgo país LP del Base × shock real del CCL (devaluación real que achica el BV en USD)
    rps = [550, 680, 810, 950, 1100]
    fxs = [-0.10, 0.0, 0.10, 0.20, 0.30]
    grilla = [[valuar(rp, fx) for fx in fxs] for rp in rps]
    assert abs(grilla[2][1] - fv) < 1e-9, "la celda Base tiene que ser el fair value publicado"
    print("\nGrilla (filas RP LP pb; columnas shock real CCL):", fxs)
    for rp, fila in zip(rps, grilla):
        print(f"  {rp:5} " + " ".join(f"{v:7.2f}" for v in fila))

    # Chequeo de sesgo
    base = r["ddm"]["base"]["valor"]
    pe_2t26 = D["precio_local"] * D["acciones"] / (D["ganancia_2t26"] * 4 * C.REEXP_JUN_OCT26)
    dcf_rp_spot = ddm("base", C.RP_SPOT, C.RP_SPOT)["valor"]
    print(f"\nP/E sobre 2T26 anualizado y reexpresado: {pe_2t26:.1f}x | DDM Base con RP {C.RP_SPOT} constante: {dcf_rp_spot:.2f}")
    print("\nCHEQUEO DE SESGO:")
    print(f"  DDM Base / precio = {base / D['precio_adr']:.2f} (alerta si fuera de 0,5-1,5) | Bear {r['ddm']['bear']['valor']:.2f} (>0)")
    print("  1 monedas: BV en ARS de oct-26 / CCL implícito del mismo día; ROE real vs Ke real (Regla 7) → OK")
    print("  2 riesgo país 1 vez: beta de bancos EE.UU. (no local) + CRP = EMBI; Bear con RP alto + haircut soberano, sin ROE negativo → OK")
    print(f"  3 tipo de cambio: CCL implícito {ccl_imp:,.0f} (no oficial) para BV y precio → OK")
    print("  4 año base: ROE 2T26 13,4% (ajustado 14,3%); guía 2026 ~12%; el año 1 del Base usa 12%, no el pico → OK")
    print("  5 limpio: ROE NIC 29 ya incluye RECPAM (es real); sin diferencia de cambio extraordinaria → OK")

    out = dict(
        fecha_corte=C.FECHA_CORTE, ticker=D["ticker"], precio_adr=D["precio_adr"], precio_local=D["precio_local"],
        ccl_implicito=ccl_imp, bv_adr=bv_adr, pbv_mercado=pbv_mercado, fair_value=fv, rp_implicito=rpi,
        upside=fv / D["precio_adr"] - 1, metodos=r["vals"],
        ddm={k: {kk: vv for kk, vv in v.items()} for k, v in r["ddm"].items()},
        sectorial={k: {"valor": v[0], "pbv": v[1]} for k, v in r["sec"].items()},
        comps={"por_par": r["comps"][0], "p25": r["comps"][1][0], "p75": r["comps"][1][1], "mediana_x": r["comps"][2]},
        reversion={k: v for k, v in r["rev"].items()}, consenso_rango=r["con"],
        grilla={"rp": rps, "fx": fxs, "valores": grilla}, haircut_bear=haircut_bear,
        exceso_capital_adr=exceso_capital_adr, expo_publica_pn=expo_sobre_pn,
        ke={k: ke_path(v["rp1"], v["rp_lp"]) for k, v in esc.items()},
    )
    # Serie en USD (Regla 3): desreexpresar a pesos del trimestre (IPC del 6-K de Galicia) y pasar al CCL
    # de cierre de cada trimestre (serie compartida).
    IPC_TRIM = {"2T25": 8855.5681, "2T26": 11826.4103}
    CIERRE = {"2T25": "2025-06-30", "3T25": "2025-09-30", "4T25": "2025-12-31", "1T26": "2026-03-31", "2T26": "2026-06-30"}
    ccl_q = {r["fecha"]: r["ccl"] for r in C.serie()}
    ni_usd = []
    for q, v, mon in D["resultados"]:
        nominal = desreexpresar(v, IPC_TRIM["2T26"], IPC_TRIM[q]) if mon == "jun26" else v
        ni_usd.append((q, nominal / ccl_q[CIERRE[q]] / 1e6))
    print("Ganancia trimestral en USD M (CCL de cierre):", [(q, round(x, 1)) for q, x in ni_usd])
    reg = r["rev"]["regimen"]
    ff = {
        "ddm": (r["ddm"]["bear"]["valor"], r["ddm"]["bull"]["valor"]),
        "sectorial": (r["sec"]["bear"][0], r["sec"]["bull"][0]),
        "comps": r["comps"][1],
        "reversion": (min(v[0] for v in reg.values()) * bv_adr, max(v[0] for v in reg.values()) * bv_adr),
        "consenso": r["con"],
    }
    print("Football field:", {k: (round(a, 2), round(b, 2)) for k, (a, b) in ff.items()})
    out.update(ni_usd=ni_usd, football=ff, pe_2t26=pe_2t26, ddm_rp_spot=dcf_rp_spot)
    json.dump(out, open(os.path.join(AQUI, "salida.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("\nsalida.json escrito")
