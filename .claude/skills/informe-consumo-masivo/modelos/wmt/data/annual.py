# Serie anual (años fiscales cerrados el 31 de enero) desde SEC EDGAR XBRL companyfacts de Walmart.
import json
d = json.load(open('facts.json'))['facts']['us-gaap']
def fy(tag, form='10-K'):
    if tag not in d: return {}
    u = d[tag]['units']; vals = u[list(u)[0]]; out = {}
    for v in vals:
        if v.get('form') != form or not v.get('end', '').endswith('-01-31'): continue
        if 'start' in v:
            y0, y1 = int(v['start'][:4]), int(v['end'][:4])
            if y1 - y0 != 1 or v['start'][5:7] != '02': continue
        out[int(v['end'][:4])] = v['val']          # la última presentación (recast) pisa a la anterior
    return out
TAGS = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'CostOfRevenue', 'SellingGeneralAndAdministrativeExpense',
        'OperatingIncomeLoss', 'NetIncomeLoss', 'NetCashProvidedByUsedInOperatingActivities', 'PaymentsToAcquirePropertyPlantAndEquipment',
        'DepreciationDepletionAndAmortization', 'DepreciationAmortizationAndAccretionNet', 'InventoryNet', 'AccountsPayableCurrent',
        'PaymentsOfDividendsCommonStock', 'PaymentsForRepurchaseOfCommonStock', 'AdvertisingExpense', 'AllocatedShareBasedCompensationExpense',
        'WeightedAverageNumberOfDilutedSharesOutstanding', 'EarningsPerShareDiluted', 'IncomeTaxExpenseBenefit',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest', 'OperatingLeaseCost',
        'InterestExpenseDebt', 'StockholdersEquity', 'Assets', 'OtherNonoperatingIncomeExpense']
res = {t: fy(t) for t in TAGS}
json.dump({t: {str(k): v for k, v in s.items()} for t, s in res.items()}, open('annual.json', 'w'), indent=1)
for t, s in res.items():
    print(t[:48].ljust(48), ' '.join(f"{y}:{v/1e9 if abs(v) > 1e6 else v:.2f}" for y, v in sorted(s.items()) if y >= 2016))
