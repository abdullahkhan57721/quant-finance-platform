# TargetCo acquisition valuation case

This portfolio case is a small, complete acquisition valuation package. It is
synthetic and intended for reviewer demonstration rather than investment advice.

## Artifacts

- `TargetCo_Acquisition_Valuation_Model.xlsx` — transparent operating model with
  assumptions, historicals, five-year forecast, FCFF, DCF, terminal value,
  enterprise-value-to-equity bridge, transaction summary, DCF sensitivity, and
  checks.
- `TargetCo_Acquisition_Valuation_Deck.pptx` — six-slide client-style summary of
  the transaction, business valuation, earnout valuation, sensitivities, risks,
  and conclusion.
- `notebooks/04_acquisition_earnout_analysis.ipynb` — output-free quantitative
  earnout analysis using the existing platform pricing infrastructure.

## Modeling boundary

The workbook owns the financial-statement-to-valuation flow. The contingent
earnout is valued in Python as a stylized cash-settled call spread on a normalized
KPI index:

```text
earnout = max_payout / (cap_strike - start_strike)
          * [Call(K=start_strike) - Call(K=cap_strike)]
```

The notebook implements that mapping by composing the platform's existing
`PricingProblem`, `BlackScholesClosedForm`, and `MonteCarloEuropeanOption`
contracts. It does not add a new stochastic model family or a second pricing
engine inside the spreadsheet.

## Case assumptions

- Dollars are shown in millions.
- TargetCo is a synthetic specialty-components business.
- The DCF uses a mid-year convention, WACC sensitivity, terminal-growth
  sensitivity, and an enterprise-value-to-equity bridge.
- The earnout has an $80mm maximum payout, a two-year maturity, a KPI index of
  100 at signing, a 115 start hurdle, and a 135 cap hurdle.

## Validation

Run:

```bash
python scripts/check_notebooks.py
pytest tests/test_portfolio_acquisition_case.py
```

The checks verify artifact structure, output-free notebook discipline, and use of
existing platform quantitative infrastructure for the earnout.
