# Balances a fin de año fiscal y otros datos puntuales de SEC XBRL, para verificar los insumos de model.py.
import json
d = json.load(open('facts.json'))['facts']['us-gaap']
def inst(tag, end):
    if tag not in d: return None
    u = d[tag]['units']; vals = u[list(u)[0]]
    r = [v['val'] for v in vals if v.get('end') == end and v.get('form') in ('10-K', '10-Q')]
    return round(r[-1]/1e9, 3) if r else None
def dur(tag, y):
    if tag not in d: return None
    u = d[tag]['units']; vals = u[list(u)[0]]
    r = [v['val'] for v in vals if v.get('end') == f'{y}-01-31' and v.get('start', '').startswith(f'{y-1}-02')]
    return r[-1] if r else None
TAGS = ['StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', 'RedeemableNoncontrollingInterestEquityCarryingAmount',
        'ShortTermBorrowings', 'LongTermDebtCurrent', 'LongTermDebtNoncurrent', 'FinanceLeaseLiabilityCurrent',
        'FinanceLeaseLiabilityNoncurrent', 'CashAndCashEquivalentsAtCarryingValue', 'InventoryNet']
for end in ('2015-01-31', '2024-01-31', '2025-01-31', '2026-01-31'):
    print(end, {t[:30]: inst(t, end) for t in TAGS})
for y in (2016, 2017):
    print('SalesRevenueNet', y, dur('SalesRevenueNet', y))
for y in (2025, 2026):
    print('Diluted shares', y, dur('WeightedAverageNumberOfDilutedSharesOutstanding', y))
