# DCF consolidado de referencia ("renovación perpetua") y DCF inverso. No entra al blend.
from scipy.optimize import brentq
def dcf(rev0, g_path, m_path, wacc, g_inf, net_debt, shares, y0=2026, stub=0.25, n=5):
    """rev0 = ingresos del año y0; g_path/m_path: crecimientos (n) y márgenes de FCF (n+1, desde y0)."""
    rev, pv, last = rev0, 0.0, None
    for i in range(n + 1):
        if i > 0: rev *= 1 + g_path[i - 1]
        f = rev * m_path[i]
        t = 0.125 if i == 0 else (i - 1) + stub + 0.5
        pv += f * (stub if i == 0 else 1) * (1 + wacc) ** -t
        last, tl = f, t
    tv = last * (1 + g_inf) / (wacc - g_inf) * (1 + wacc) ** -tl   # Gordon descontado como el último flujo (mitad de año)
    ev = pv + tv
    return dict(fv=(ev - net_debt) / shares, tv_share=tv / ev, rev_last=rev, ev=ev)
def lin_path(a, b, n): return [a + (b - a) * i / (n - 1) for i in range(n)]
def implied_g(price, rev0, m_path, wacc, g_inf, net_debt, shares, g_last=None):
    f = lambda g: dcf(rev0, [g] * 5, m_path, wacc, g_inf, net_debt, shares)['fv'] - price
    return brentq(f, -0.5, 1.0)
if __name__ == '__main__':
    m = lin_path(0.275, 0.36, 6)
    r = dcf(86.6, lin_path(0.074, 0.035, 5), m, 0.0822, 0.03, 45.958, 0.894)
    print('sep DCF', round(r['fv'], 2), 'tv', round(r['tv_share'] * 100, 1), 'target 723.66 / 80.6%')
    g = implied_g(1150.99, 86.6, m, 0.0822, 0.03, 45.958, 0.894)
    print('implied g', round(g * 100, 2), 'rev2031', round(86.6 * (1 + g) ** 5, 1), 'target 16.2% / 183.7')
