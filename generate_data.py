import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# --- Leads dataset ---
n_leads = 500
segments = ['Enterprise', 'Mid-Market', 'SMB']
seg_weights = [0.2, 0.35, 0.45]
regions = ['EMEA', 'AMER', 'APAC']
sources = ['Inbound', 'Outbound', 'Partner', 'Event']
industries = ['Public Sector', 'Professional Services', 'Manufacturing', 'Healthcare', 'Education']

start_date = datetime(2023, 1, 1)

def rand_date(start, days=730):
    return start + timedelta(days=random.randint(0, days))

leads = []
for i in range(n_leads):
    seg = np.random.choice(segments, p=seg_weights)
    created = rand_date(start_date)
    
    # Conversion probabilities by segment
    conv_p = {'Enterprise': 0.38, 'Mid-Market': 0.27, 'SMB': 0.14}[seg]
    became_opp = random.random() < conv_p
    
    opp_date = created + timedelta(days=random.randint(5, 30)) if became_opp else None
    
    close_p = {'Enterprise': 0.52, 'Mid-Market': 0.40, 'SMB': 0.28}[seg]
    won = (became_opp and random.random() < close_p)
    
    close_date = opp_date + timedelta(days=random.randint(30, 180)) if opp_date else None
    
    # Deal size by segment
    if seg == 'Enterprise':
        deal = round(np.random.normal(120000, 40000), -3) if won else None
    elif seg == 'Mid-Market':
        deal = round(np.random.normal(45000, 15000), -3) if won else None
    else:
        deal = round(np.random.normal(12000, 4000), -3) if won else None

    deal = max(deal, 5000) if deal else None

    leads.append({
        'lead_id': f'L{1000+i}',
        'created_date': created.strftime('%Y-%m-%d'),
        'segment': seg,
        'region': np.random.choice(regions),
        'source': np.random.choice(sources),
        'industry': np.random.choice(industries),
        'became_opportunity': became_opp,
        'opportunity_date': opp_date.strftime('%Y-%m-%d') if opp_date else None,
        'closed_won': won,
        'close_date': close_date.strftime('%Y-%m-%d') if close_date else None,
        'deal_value_eur': deal,
        'sales_rep': f'Rep_{random.randint(1,12)}',
    })

df_leads = pd.DataFrame(leads)

# --- Customers / Retention dataset ---
n_customers = 200
cohort_months = ['2022-Q1','2022-Q2','2022-Q3','2022-Q4','2023-Q1','2023-Q2','2023-Q3','2023-Q4']

customers = []
for i in range(n_customers):
    seg = np.random.choice(segments, p=seg_weights)
    cohort = np.random.choice(cohort_months)
    arr = {'Enterprise': round(np.random.normal(110000,30000),-3),
           'Mid-Market': round(np.random.normal(42000,12000),-3),
           'SMB': round(np.random.normal(11000,3000),-3)}[seg]
    arr = max(arr, 4000)
    
    churn_p = {'Enterprise': 0.07, 'Mid-Market': 0.13, 'SMB': 0.22}[seg]
    churned = random.random() < churn_p
    
    # NPS score
    nps = np.random.randint(0,11)
    
    customers.append({
        'customer_id': f'C{2000+i}',
        'segment': seg,
        'region': np.random.choice(regions),
        'industry': np.random.choice(industries),
        'cohort': cohort,
        'arr_eur': arr,
        'churned': churned,
        'nps_score': nps,
        'support_tickets_6m': np.random.randint(0, 15),
        'last_login_days_ago': np.random.randint(1, 180) if not churned else np.random.randint(60, 365),
    })

df_customers = pd.DataFrame(customers)

df_leads.to_csv('/home/claude/revops-funnel-analysis/data/leads_pipeline.csv', index=False)
df_customers.to_csv('/home/claude/revops-funnel-analysis/data/customers_retention.csv', index=False)
print("Datasets generated!")
print(f"Leads: {len(df_leads)} rows")
print(f"Customers: {len(df_customers)} rows")
