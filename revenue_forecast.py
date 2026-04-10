"""
RevOps Case Study – Revenue Forecast Model
Three scenarios (Optimistic / Base / Pessimistic) by segment
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    'Enterprise': '#1B3A6B',
    'Mid-Market': '#2E86AB',
    'SMB':        '#A8DADC',
    'optimistic': '#2E7D32',
    'base':       '#1B3A6B',
    'pessimistic':'#E63946',
    'neutral':    '#F1FAEE',
}

leads = pd.read_csv('../data/leads_pipeline.csv', parse_dates=['created_date','close_date'])

# ── 1. HISTORICAL MONTHLY REVENUE ────────────────────────────
won = leads[leads['closed_won']].copy()
won['month'] = won['close_date'].dt.to_period('M')
monthly = won.groupby(['month','segment'])['deal_value_eur'].sum().reset_index()
monthly['month_dt'] = monthly['month'].dt.to_timestamp()
monthly['month_num'] = (monthly['month_dt'].dt.year - 2023) * 12 + monthly['month_dt'].dt.month

# Overall monthly total
monthly_total = won.groupby('month')['deal_value_eur'].sum().reset_index()
monthly_total['month_dt'] = monthly_total['month'].dt.to_timestamp()
monthly_total['month_num'] = (monthly_total['month_dt'].dt.year - 2023) * 12 + monthly_total['month_dt'].dt.month
monthly_total = monthly_total.sort_values('month_num')

# ── 2. LINEAR TREND ──────────────────────────────────────────
x = monthly_total['month_num'].values
y = monthly_total['deal_value_eur'].values
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

print(f"Trend: slope=€{slope:,.0f}/month | R²={r_value**2:.2f} | p={p_value:.3f}")

# ── 3. FORECAST PERIODS (next 6 months) ──────────────────────
last_month = monthly_total['month_num'].max()
forecast_months = list(range(last_month + 1, last_month + 7))
forecast_labels = []
for m in forecast_months:
    year = 2023 + (m - 1) // 12
    month = ((m - 1) % 12) + 1
    forecast_labels.append(f"{year}-{month:02d}")

# Base scenario — linear trend
base = [max(0, slope * m + intercept) for m in forecast_months]

# Optimistic — +20% on base (pipeline acceleration)
optimistic = [b * 1.20 for b in base]

# Pessimistic — -25% on base (churn impact + slower pipeline)
pessimistic = [b * 0.75 for b in base]

forecast_df = pd.DataFrame({
    'month': forecast_labels,
    'month_num': forecast_months,
    'base': base,
    'optimistic': optimistic,
    'pessimistic': pessimistic,
})

# ── 4. SEGMENT FORECAST ──────────────────────────────────────
seg_forecast = {}
for seg in ['Enterprise', 'Mid-Market', 'SMB']:
    seg_data = monthly[monthly['segment'] == seg].sort_values('month_num')
    if len(seg_data) < 3:
        continue
    xs = seg_data['month_num'].values
    ys = seg_data['deal_value_eur'].values
    sl, inter, rv, _, _ = stats.linregress(xs, ys)
    seg_base = [max(0, sl * m + inter) for m in forecast_months]
    seg_forecast[seg] = {
        'base':        seg_base,
        'optimistic':  [b * 1.20 for b in seg_base],
        'pessimistic': [b * 0.75 for b in seg_base],
        'slope': sl,
        'r2': rv**2,
    }

# ── 5. PRINT SUMMARY ─────────────────────────────────────────
print("\n=== 6-MONTH REVENUE FORECAST SUMMARY ===")
print(f"{'Month':<12} {'Pessimistic':>14} {'Base':>14} {'Optimistic':>14}")
for _, row in forecast_df.iterrows():
    print(f"{row['month']:<12} €{row['pessimistic']:>12,.0f} €{row['base']:>12,.0f} €{row['optimistic']:>12,.0f}")

total_base = sum(base)
total_opt  = sum(optimistic)
total_pess = sum(pessimistic)
print(f"\n{'6M TOTAL':<12} €{total_pess:>12,.0f} €{total_base:>12,.0f} €{total_opt:>12,.0f}")

print("\n=== SEGMENT TRENDS ===")
for seg, data in seg_forecast.items():
    print(f"{seg:<14} slope=€{data['slope']:,.0f}/month | R²={data['r2']:.2f} | 6M base=€{sum(data['base']):,.0f}")

# ── 6. DASHBOARD ─────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('RevOps Case Study — Revenue Forecast Model', fontsize=16, fontweight='bold')
fig.patch.set_facecolor('#FAFAFA')

hist_labels = [str(m) for m in monthly_total['month'].values]
hist_rev    = monthly_total['deal_value_eur'].values

# Panel 1: Historical + trend line
ax1 = axes[0, 0]
ax1.bar(range(len(hist_labels)), hist_rev, color=COLORS['base'], alpha=0.6, label='Actual')
trend_line = [slope * m + intercept for m in monthly_total['month_num'].values]
ax1.plot(range(len(hist_labels)), trend_line, color=COLORS['pessimistic'],
         linewidth=2, linestyle='--', label=f'Trend (R²={r_value**2:.2f})')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1000:.0f}k'))
step = max(1, len(hist_labels) // 8)
ax1.set_xticks(range(0, len(hist_labels), step))
ax1.set_xticklabels(hist_labels[::step], rotation=45, ha='right', fontsize=7)
ax1.set_title('Historical Revenue + Trend Line', fontweight='bold')
ax1.legend(fontsize=8)
ax1.set_facecolor(COLORS['neutral'])

# Panel 2: 3-scenario forecast
ax2 = axes[0, 1]
x_f = range(len(forecast_labels))
ax2.fill_between(x_f, pessimistic, optimistic, alpha=0.15, color=COLORS['base'], label='Range')
ax2.plot(x_f, optimistic,  color=COLORS['optimistic'],  linewidth=2, marker='o', label='Optimistic (+20%)')
ax2.plot(x_f, base,        color=COLORS['base'],        linewidth=2, marker='o', label='Base (trend)')
ax2.plot(x_f, pessimistic, color=COLORS['pessimistic'], linewidth=2, marker='o', label='Pessimistic (-25%)')
ax2.set_xticks(list(x_f))
ax2.set_xticklabels(forecast_labels, rotation=45, ha='right', fontsize=8)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1000:.0f}k'))
ax2.set_title('6-Month Revenue Forecast — 3 Scenarios', fontweight='bold')
ax2.legend(fontsize=8)
ax2.set_facecolor(COLORS['neutral'])

# Panel 3: Segment forecast (base scenario)
ax3 = axes[1, 0]
for seg, data in seg_forecast.items():
    ax3.plot(x_f, data['base'], marker='o', linewidth=2,
             color=COLORS[seg], label=seg)
ax3.set_xticks(list(x_f))
ax3.set_xticklabels(forecast_labels, rotation=45, ha='right', fontsize=8)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1000:.0f}k'))
ax3.set_title('Forecast by Segment — Base Scenario', fontweight='bold')
ax3.legend(fontsize=8)
ax3.set_facecolor(COLORS['neutral'])

# Panel 4: 6M total by scenario (bar chart)
ax4 = axes[1, 1]
scenarios = ['Pessimistic\n(-25%)', 'Base\n(trend)', 'Optimistic\n(+20%)']
totals    = [total_pess, total_base, total_opt]
bar_colors = [COLORS['pessimistic'], COLORS['base'], COLORS['optimistic']]
bars = ax4.bar(scenarios, totals, color=bar_colors, width=0.5)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1000:.0f}k'))
ax4.set_title('6-Month Total Revenue by Scenario', fontweight='bold')
ax4.set_facecolor(COLORS['neutral'])
for bar in bars:
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
             f'€{bar.get_height():,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
out_path = os.path.join(OUTPUT_DIR, 'revenue_forecast.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nForecast dashboard saved → {out_path}")

# Save forecast data for Excel
forecast_df.to_csv(os.path.join(OUTPUT_DIR, 'forecast_data.csv'), index=False)

# Save segment forecast
seg_rows = []
for seg, data in seg_forecast.items():
    for i, m in enumerate(forecast_labels):
        seg_rows.append({
            'month': m, 'segment': seg,
            'pessimistic': data['pessimistic'][i],
            'base': data['base'][i],
            'optimistic': data['optimistic'][i],
        })
pd.DataFrame(seg_rows).to_csv(os.path.join(OUTPUT_DIR, 'forecast_by_segment.csv'), index=False)
print("Forecast CSVs saved for Excel ingestion.")
