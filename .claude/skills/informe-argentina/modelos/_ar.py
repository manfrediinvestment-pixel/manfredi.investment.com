"""Funciones comunes para valuar acciones argentinas — skill informe-argentina.

Uso desde modelos/<ticker>/valuacion.py:
    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from _ar import *

Todas las tasas en decimales (0.085 = 8.5%), riesgo país en puntos básicos (850 = 8.5%).
Correr `python _ar.py` ejecuta las pruebas de cordura.
"""

# ---------- Costo de capital ----------

def ke_usd(rf, beta, erp, crp_pb, lam=1.0):
    """Ke en USD = Rf + beta*ERP maduro + lambda*CRP. crp_pb en puntos básicos."""
    return rf + beta * erp + lam * crp_pb / 10000


def beta_reapalancada(beta_u, deuda, equity, tasa_imp=0.35):
    """Hamada: beta de la industria global desapalancada → estructura de la empresa."""
    return beta_u * (1 + (1 - tasa_imp) * deuda / equity)


def wacc(ke, kd, deuda, equity, tasa_imp=0.35):
    v = deuda + equity
    return ke * equity / v + kd * (1 - tasa_imp) * deuda / v


def crp_path(crp_año1, crp_lp, n=5):
    """Senda lineal de riesgo país (pb) del año 1 al n; el terminal usa crp_lp."""
    if n == 1:
        return [crp_lp]
    return [crp_año1 + (crp_lp - crp_año1) * i / (n - 1) for i in range(n)]


def ke_real(ke_usd_, infl_usa=0.025):
    """Ke en USD → Ke real (para comparar con ROE real NIC 29). Supone PPA de largo plazo."""
    return (1 + ke_usd_) / (1 + infl_usa) - 1


# ---------- DCF en USD con tasa variable ----------

def dcf_usd(fcf, tasas, g, tasa_terminal=None, deuda_neta=0.0, acciones=1.0):
    """FCF anuales en USD descontados con una tasa distinta por año (senda de riesgo país).

    tasas: lista del mismo largo que fcf (Ke o WACC de cada año).
    tasa_terminal: tasa del valor terminal (default: la del último año).
    Devuelve dict con valor por acción, EV y % del EV desde el terminal.
    """
    assert len(fcf) == len(tasas)
    factor, pv = 1.0, 0.0
    for f, r in zip(fcf, tasas):
        factor *= 1 + r
        pv += f / factor
    rt = tasa_terminal if tasa_terminal is not None else tasas[-1]
    assert rt > g, "la tasa terminal tiene que superar al crecimiento"
    tv = fcf[-1] * (1 + g) / (rt - g) / factor
    ev = pv + tv
    return {"por_accion": (ev - deuda_neta) / acciones, "ev": ev, "pct_terminal": tv / ev}


def tasas_desde_crp(rf, beta, erp, crp_año1, crp_lp, lam=1.0, n=5, kd=None, deuda=0.0,
                    equity=1.0, tasa_imp=0.35):
    """Arma la lista de Ke (o WACC si se pasa kd) año a año siguiendo la senda de CRP."""
    out = []
    for c in crp_path(crp_año1, crp_lp, n):
        k = ke_usd(rf, beta, erp, c, lam)
        out.append(wacc(k, kd, deuda, equity, tasa_imp) if kd is not None else k)
    return out


# ---------- Contabilidad NIC 29 ----------

def trimestre_standalone(ytd_t, ytd_prev, ipc_t, ipc_prev):
    """Trimestre aislado en moneda de cierre t: YTD_t − YTD_{t−1} reexpresado a t."""
    return ytd_t - ytd_prev * (ipc_t / ipc_prev)


def desreexpresar(valor_cierre, ipc_cierre, ipc_periodo):
    """Moneda de cierre → pesos nominales del período."""
    return valor_cierre * ipc_periodo / ipc_cierre


def a_usd(valor_cierre, ipc_cierre, ipc_periodo, fx_periodo):
    """Cifra NIC 29 en moneda de cierre → USD al tipo de cambio del período."""
    return desreexpresar(valor_cierre, ipc_cierre, ipc_periodo) / fx_periodo


def variacion_real(actual, anterior_nominal, ipc_actual, ipc_anterior):
    """Variación real entre dos cifras en pesos nominales de distintas fechas."""
    return actual / (anterior_nominal * ipc_actual / ipc_anterior) - 1


# ---------- Mercado ----------

def ccl_implicito(precio_local_ars, ratio, precio_adr_usd):
    return precio_local_ars * ratio / precio_adr_usd


def brecha(fx_paralelo, fx_oficial):
    return fx_paralelo / fx_oficial - 1


# ---------- Métodos de valuación ----------

def pbv_justificado(roe_real, g_real, ke_usd_, infl_usa=0.025):
    """P/BV justificado de un banco con ROE real (NIC 29) y Ke en USD pasado a real."""
    kr = ke_real(ke_usd_, infl_usa)
    assert kr > g_real
    return (roe_real - g_real) / (kr - g_real)


def multiplo_ajustado_por_pais(multiplo_peer, ke_peer, ke_ar, g):
    """Descuento país justificado: escala el múltiplo del peer por el diferencial de Ke."""
    return multiplo_peer * (ke_peer - g) / (ke_ar - g)


def sotp_holding(partes, deuda_neta_holding, acciones, descuento=0.15):
    """partes: dict nombre -> valor en USD de la participación (ya × % de tenencia)."""
    bruto = sum(partes.values()) - deuda_neta_holding
    return bruto * (1 - descuento) / acciones


def riesgo_pais_implicito(precio, valuar, lo=0, hi=5000, tol=0.01):
    """DCF inverso: el CRP de largo plazo (pb) que hace valuar(crp) == precio.

    valuar: función crp_pb -> valor por acción (decreciente en crp). Bisección.
    Devuelve None si el precio cae fuera del rango [valuar(hi), valuar(lo)].
    """
    vlo, vhi = valuar(lo), valuar(hi)
    if not (vhi <= precio <= vlo):
        return None
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if valuar(mid) > precio:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def esperado(escenarios, probs=(0.25, 0.50, 0.25)):
    """Valor esperado de (bear, base, bull)."""
    return sum(v * p for v, p in zip(escenarios, probs))


PESOS_BLEND = {"dcf": 0.15, "sectorial": 0.15, "comps": 0.20, "reversion": 0.30, "consenso": 0.20}


def blend(valores, pesos=PESOS_BLEND):
    """Promedio ponderado. Si falta 'sectorial', su peso pasa al DCF."""
    p = dict(pesos)
    if "sectorial" not in valores:
        p["dcf"] += p.pop("sectorial")
    assert abs(sum(p.values()) - 1) < 1e-9 and set(p) == set(valores), (p, valores)
    return sum(valores[k] * p[k] for k in p)


# ---------- Pruebas de cordura ----------

if __name__ == "__main__":
    # Ke: 4.3% + 1.0*5% + 1.0*850pb = 17.8%
    k = ke_usd(0.043, 1.0, 0.05, 850)
    assert abs(k - 0.178) < 1e-12
    assert crp_path(900, 500) == [900, 800, 700, 600, 500]

    # Trimestre NIC 29: YTD 9M = 300 (moneda sep), YTD 6M = 180 (moneda jun), IPC +10% en el trim.
    assert abs(trimestre_standalone(300, 180, 110, 100) - 102) < 1e-9

    # Desreexpresar y pasar a USD: 1.100 en moneda de cierre, IPC cierre 110, período 100, fx 1.000
    assert abs(a_usd(1100, 110, 100, 1000) - 1.0) < 1e-12

    assert abs(ccl_implicito(7500, 10, 50) - 1500) < 1e-9

    # DCF con tasa constante = Gordon clásico
    r = dcf_usd([100] * 5, [0.10] * 5, 0.0)
    gordon = sum(100 / 1.1 ** t for t in range(1, 6)) + 100 / 0.10 / 1.1 ** 5
    assert abs(r["ev"] - gordon) < 1e-6

    # Riesgo país implícito: debe recuperar el CRP con el que se generó el precio
    def val(crp):
        t = tasas_desde_crp(0.043, 1.0, 0.05, 850, crp)
        return dcf_usd([100, 110, 120, 128, 135], t, 0.025, acciones=10)["por_accion"]
    p = val(700)
    assert abs(riesgo_pais_implicito(p, val) - 700) < 0.05

    # P/BV justificado: ROE real 17%, g real 3%, Ke USD 17.8% → Ke real 14.93%
    m = pbv_justificado(0.17, 0.03, 0.178)
    assert 1.15 < m < 1.20, m

    # Múltiplo peer 6x con Ke 12% → Argentina Ke 17.8%, g 2.5% → ~3.7x
    assert abs(multiplo_ajustado_por_pais(6, 0.12, 0.178, 0.025) - 6 * 0.095 / 0.153) < 1e-12

    assert abs(blend({"dcf": 10, "sectorial": 10, "comps": 10, "reversion": 10, "consenso": 10}) - 10) < 1e-12
    assert abs(blend({"dcf": 10, "comps": 20, "reversion": 20, "consenso": 20}) - (3 + 4 + 6 + 4)) < 1e-12

    print("ok — _ar.py: todas las pruebas pasan")
    print("ejemplo: Ke USD con riesgo país 850 pb =", round(k * 100, 2), "%;",
          "P/BV justificado ROE real 17% =", round(m, 2), "x;",
          "riesgo país implícito del ejemplo =", round(riesgo_pais_implicito(p, val)), "pb")
