# Captura "páginas" reales de los informes (zona de un gráfico) para el clip de cierre.
# Uso: python capturar-paginas.py   -> cierre/paginas/p1..pN.png
import pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).parent / "cierre" / "paginas"
PICKS = [("nvda", "historyChart"), ("msft", "marginChart"), ("aapl", "segmentChart"), ("meli", "historyChart"),
         ("ko", "marginChart"), ("googl", "segmentChart"), ("tsla", "historyChart"), ("lly", "marginChart")]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 800, "height": 1040}, device_scale_factor=1.5)
    n = 0
    for t, cid in PICKS:
        pg.goto((ROOT / "informes" / f"{t}.html").as_uri() + "?preview=full")
        pg.wait_for_timeout(1200)
        el = pg.query_selector(f"#{cid}") or pg.query_selector("canvas")
        if not el: print("sin canvas", t); continue
        # subir hasta el título de la sección para que la página tenga contexto
        pg.evaluate("""el => { const s = el.closest('section') || el.parentElement;
            const h = s.querySelector('h2,h3') || el; window.scrollTo(0, h.getBoundingClientRect().top + scrollY - 30); }""", el)
        pg.wait_for_timeout(400)
        n += 1
        pg.screenshot(path=str(OUT / f"p{n}.png"))
        print("ok", t, cid)
    b.close()
