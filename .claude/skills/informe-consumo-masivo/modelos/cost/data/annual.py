# Serie anual (años fiscales de 52/53 semanas que cierran el domingo más cercano al 31 de agosto) desde SEC EDGAR XBRL
# companyfacts de Costco (facts.json, bajado por fetch_sec.py). La última presentación (recast) pisa a la anterior.
import json
d = json.load(open('facts.json'))['facts']['us-gaap']
def fy(tags, flow=True):
    out = {}
    for tag in tags if isinstance(tags, list) else [tags]:
        if tag not in d: continue
        u = d[tag]['units']; vals = u[list(u)[0]]
        for v in sorted(vals, key=lambda x: x.get('filed', '')):
            if v.get('form') != '10-K': continue
            e = v.get('end', '')
            if e[5:7] not in ('08', '09'): continue
            y = int(e[:4]) if e[5:7] == '08' or e[8:10] <= '07' else None
            if y is None: continue
            if flow:
                if 'start' not in v: continue
                days = (int(e[:4]) - int(v['start'][:4]))*365 + (int(e[5:7]) - int(v['start'][5:7]))*30 + int(e[8:10]) - int(v['start'][8:10])
                if not 350 <= days <= 380: continue
            elif 'start' in v: continue
            if y not in out or tag == (tags[0] if isinstance(tags, list) else tags): out[y] = v['val']
    return out
FLOW = {
 'Revenues': ['Revenues'],
 'NetSales': ['RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueGoodsNet', 'SalesRevenueNet'],
 'MerchCosts': ['CostOfGoodsAndServicesSold', 'CostOfRevenue', 'CostOfGoodsSold'],
 'SGA': ['SellingGeneralAndAdministrativeExpense'],
 'OI': ['OperatingIncomeLoss'],
 'NI': ['NetIncomeLoss', 'IncomeLossAttributableToParent'],
 'OCF': ['NetCashProvidedByUsedInOperatingActivities'],
 'Capex': ['PaymentsToAcquirePropertyPlantAndEquipment'],
 'DA': ['DepreciationDepletionAndAmortization', 'DepreciationAmortizationAndAccretionNet'],
 'Div': ['PaymentsOfDividendsCommonStock', 'PaymentsOfDividends'],
 'Buyback': ['PaymentsForRepurchaseOfCommonStock'],
 'SBC': ['ShareBasedCompensation'],
 'DilShares': ['WeightedAverageNumberOfDilutedSharesOutstanding'],
 'EPSDil': ['EarningsPerShareDiluted'],
 'Tax': ['IncomeTaxExpenseBenefit'],
 'PreTax': ['IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'],
 'IntExp': ['InterestExpense', 'InterestExpenseNonoperating'],
 'DivPS': ['CommonStockDividendsPerShareDeclared'],
}
STOCK = {
 'Inventory': ['InventoryNet'], 'AP': ['AccountsPayableCurrent'], 'Cash': ['CashAndCashEquivalentsAtCarryingValue'],
 'STInv': ['ShortTermInvestments'], 'Equity': ['StockholdersEquity'], 'EquityTot': ['StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
 'LTDebt': ['LongTermDebtNoncurrent'], 'LTDebtCur': ['LongTermDebtCurrent'], 'Assets': ['Assets'],
 'FinLease': ['FinanceLeaseLiability'], 'OpLease': ['OperatingLeaseLiability'], 'DefMemb': ['ContractWithCustomerLiabilityCurrent'],
}
res = {k: fy(v) for k, v in FLOW.items()}
res.update({k: fy(v, flow=False) for k, v in STOCK.items()})
json.dump({t: {str(k): v for k, v in sorted(s.items())} for t, s in res.items()}, open('annual.json', 'w'), indent=1)
if __name__ == '__main__':
    for t, s in res.items():
        print(t.ljust(11), ' '.join(f"{y}:{v/1e9 if abs(v) > 1e6 else v:.3f}" for y, v in sorted(s.items()) if y >= 2014))
