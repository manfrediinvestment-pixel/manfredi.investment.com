# 10-K FY2026 (31-ene-2026), 10-Q 1T y 2T FY2027 y proxy 2026, como texto.
from fetch_sec import get, txt
DOCS = {
    '10k_fy26.txt': '000010416926000055/wmt-20260131.htm',
    '10q_q2fy27.txt': '000010416926000154/wmt-20260731.htm',
    '10q_q1fy27.txt': '000010416926000102/wmt-20260430.htm',
    'proxy26.txt': '000119312526173673/wmt-20260423.htm',
    '10k_fy25.txt': '000010416925000021/wmt-20250131.htm',
}
for out, path in DOCS.items():
    open(out, 'w', encoding='utf-8').write(txt(get('https://www.sec.gov/Archives/edgar/data/104169/' + path)))
    print(out)
