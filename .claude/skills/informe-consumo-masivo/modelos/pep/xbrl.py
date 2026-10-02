# Extrae de companyfacts (SEC XBRL) las series anuales (10-K, FY) y semestrales (10-Q 2T) que usa model.py.
# Uso: python xbrl.py  -> imprime una tabla para revisar y guarda raw/xbrl_series.json
import json
from datetime import date
cf = json.load(open('raw/companyfacts.json'))['facts']
def series(tag, ns='us-gaap', unit='USD'):
    try: units = cf[ns][tag]['units'][unit]
    except KeyError: return {}, {}
    ann, h1 = {}, {}
    for u in units:
        fp, form, fy = u.get('fp'), u.get('form'), u.get('fy')
        s, e = u.get('start'), u['end']
        if form == '10-K' and fp == 'FY' and s:
            days = (date.fromisoformat(e) - date.fromisoformat(s)).days
            if 350 < days < 380: ann[int(e[:4])] = u['val']
        if form == '10-Q' and fp == 'Q2' and s and 170 < (date.fromisoformat(e) - date.fromisoformat(s)).days < 200:
            h1[e[:7]] = u['val']
    return ann, h1
TAGS = {
 'rev': 'Revenues', 'rev2': 'RevenueFromContractWithCustomerExcludingAssessedTax', 'cogs': 'CostOfGoodsAndServicesSold',
 'sga': 'SellingGeneralAndAdministrativeExpense', 'oi': 'OperatingIncomeLoss', 'ni': 'NetIncomeLoss',
 'ocf': 'NetCashProvidedByUsedInOperatingActivities', 'capex': 'PaymentsToAcquirePropertyPlantAndEquipment',
 'div': 'PaymentsOfDividendsCommonStock', 'div2': 'PaymentsOfDividends', 'buy': 'PaymentsForRepurchaseOfCommonStock',
 'da': 'DepreciationDepletionAndAmortization', 'adv': 'AdvertisingExpense', 'eqinc': 'IncomeLossFromEquityMethodInvestments',
 'eqdiv': 'ProceedsFromEquityMethodInvestmentDividendsOrDistributions', 'sbc': 'ShareBasedCompensation',
 'intexp': 'InterestExpense', 'intexp2': 'InterestExpenseNonoperating', 'tax': 'IncomeTaxExpenseBenefit', 'pretax': 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
 'otherop': 'OtherCostAndExpenseOperating',
}
out = {}
for k, t in TAGS.items():
    a, h = series(t); out[k] = {'ann': a, 'h1': h}
    print(f"{k:8s} {t[:40]:40s}", {y: round(v/1e6) for y, v in sorted(a.items()) if y >= 2014}, {y: round(v/1e6) for y, v in sorted(h.items()) if y >= '2024'})
json.dump(out, open('raw/xbrl_series.json', 'w'), indent=0)
