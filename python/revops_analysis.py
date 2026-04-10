"""
RevOps Case Study – Funnel & Retention Analysis
Unit4 Revenue Operations Business Partner | Portfolio Project
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {
    'Enterprise': '#1B3A6B',
    'Mid-Market': '#2E86AB',
    'SMB':        '#A8DADC',
    'accent':     '#E63946',
    'neutral':    '#F1FAEE',
}

leads = pd.read_csv('../data/leads_pipeline.csv', parse_dates=['created_date','opportunity_date','close_date'])
customers = pd.read_csv('../data/customers_retention.csv')

# ── 1. FUNNEL CONVERSION BY SEGMENT ──────────────────────────────────────────
funnel = leads.groupby('segment').agg(
    total_leads=('lead_id', 'count'),
    opportunities=('became_opportunity', 'sum'),
    won=('closed_won', 'sum'),
).reset_index()

funnel['lead_opp_pct']   = funnel['opportunities'] / funnel['total_leads']
funnel['opp_close_pct']  = funnel['won'] / funnel['opportunities']
funnel['overall_win_pct'] = funnel['won'] / funnel['total_leads']

# ── 2. REVENUE SUMMARY ───────────────────────────────────────────────────────
won_deals = leads[leads['closed_won']].copy()
revenue = won_deals.groupby('segment').agg(
    deals=('lead_id', 'count'),
    total_rev=('deal_value_eur', 'sum'),
    avg_deal=('deal_value_eur', 'mean'),
).reset_index()

# ── 3. CHURN BY SEGMENT ──────────────────────────────────────────────────────
churn = customers.groupby('segment').agg(
    total=('customer_id', 'count'),
    churned=('churned', 'sum'),
    total_arr=('arr_eur', 'sum'),
).reset_index()
churn['churn_rate'] = churn['churned'] / churn['total']

# ── 4. MONTHLY PIPELINE TREND ────────────────────────────────────────────────
leads['month'] = leads['created_date'].dt.to_period('M')
monthly = leads.groupby('month').agg(
    leads_created=('lead_id', 'count'),
    opps=('became_opportunity', 'sum'),
    won=('closed_won', 'sum'),
    revenue=('deal_value_eur', 'sum'),
).reset_index()
monthly['month_str'] = monthly['month'].astype(str)

# ── PLOT: 4-panel dashboard ──────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle('RevOps Case Study – Funnel & Retention Dashboard', fontsize=16, fontweight='bold', y=1.01)
fig.patch.set_facecolor('#FAFAFA')

# Panel 1: Win rates by segment
ax1 = axes[0, 0]
segs = funnel['segment']
x = range(len(segs))
w = 0.28
bars1 = ax1.bar([i - w for i in x], funnel['lead_opp_pct'],  width=w, label='Lead → Opp',   color=COLORS['Enterprise'])
bars2 = ax1.bar([i       for i in x], funnel['opp_close_pct'],  width=w, label='Opp → Close', color=COLORS['Mid-Market'])
bars3 = ax1.bar([i + w for i in x], funnel['overall_win_pct'], width=w, label='Overall Win',  color=COLORS['SMB'])
ax1.set_xticks(list(x))
ax1.set_xticklabels(segs)
ax1.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax1.set_title('Funnel Conversion Rates by Segment', fontweight='bold')
ax1.legend(fontsize=8)
ax1.set_facecolor(COLORS['neutral'])

# Panel 2: Average deal size
ax2 = axes[0, 1]
bars = ax2.bar(revenue['segment'], revenue['avg_deal'],
               color=[COLORS['Enterprise'], COLORS['Mid-Market'], COLORS['SMB']])
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v:,.0f}'))
ax2.set_title('Average Deal Size by Segment (EUR)', fontweight='bold')
ax2.set_facecolor(COLORS['neutral'])
for bar in bars:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
             f'€{bar.get_height():,.0f}', ha='center', va='bottom', fontsize=9)

# Panel 3: Churn rate by segment
ax3 = axes[1, 0]
bars = ax3.bar(churn['segment'], churn['churn_rate'],
               color=[COLORS['accent'] if r > 0.15 else COLORS['Mid-Market']
                      for r in churn['churn_rate']])
ax3.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax3.set_title('Churn Rate by Segment ⚠ High = Risk', fontweight='bold')
ax3.set_facecolor(COLORS['neutral'])
ax3.axhline(0.15, color='red', linestyle='--', linewidth=1, alpha=0.6, label='15% threshold')
ax3.legend(fontsize=8)

# Panel 4: Monthly revenue trend
ax4 = axes[1, 1]
months_plot = monthly[monthly['revenue'].notna()]
ax4.plot(months_plot['month_str'], months_plot['revenue'], marker='o',
         color=COLORS['Enterprise'], linewidth=2)
ax4.fill_between(months_plot['month_str'], months_plot['revenue'],
                 alpha=0.15, color=COLORS['Enterprise'])
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'€{v/1000:.0f}k'))
ax4.set_title('Monthly Closed Revenue (EUR)', fontweight='bold')
ax4.set_facecolor(COLORS['neutral'])
tick_step = max(1, len(months_plot) // 8)
ax4.set_xticks(range(0, len(months_plot), tick_step))
ax4.set_xticklabels(months_plot['month_str'].iloc[::tick_step], rotation=45, ha='right', fontsize=8)

plt.tight_layout()
out_path = os.path.join(OUTPUT_DIR, 'revops_dashboard.png')
plt.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"Dashboard saved → {out_path}")

# ── PRINT KEY INSIGHTS ───────────────────────────────────────────────────────
print("\n=== KEY INSIGHTS ===")
for _, row in funnel.iterrows():
    print(f"{row['segment']:12s} | Lead→Opp: {row['lead_opp_pct']:.0%} | Opp→Close: {row['opp_close_pct']:.0%} | Overall: {row['overall_win_pct']:.0%}")

print("\n=== REVENUE ===")
for _, row in revenue.iterrows():
    print(f"{row['segment']:12s} | Deals: {row['deals']:3.0f} | Total: €{row['total_rev']:,.0f} | Avg: €{row['avg_deal']:,.0f}")

print("\n=== CHURN ===")
for _, row in churn.iterrows():
    print(f"{row['segment']:12s} | Churn: {row['churn_rate']:.0%} | ARR at risk: €{row['churned'] * row['total_arr']/row['total']:,.0f}")
