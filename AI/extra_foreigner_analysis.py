"""
AI/extra_foreigner_analysis.py
Creates additional foreigners plots and tables using `filtered_data/foreigners_recalculated.csv`.
Writes outputs to `AI/results/` only.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AI_RESULTS = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(AI_RESULTS, exist_ok=True)

infile = os.path.join(ROOT, 'filtered_data', 'foreigners_recalculated.csv')
if not os.path.exists(infile):
    raise FileNotFoundError(infile)

df = pd.read_csv(infile, encoding='utf-8-sig')
# Normalize
df.columns = df.columns.str.strip()
for c in ['장기외국인수','단기외국인수','전체외국인수','지역인구','외국인비율(%)']:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

# Compute proportions (short vs long of total foreigners)
df['long_pct'] = df['장기외국인수'] / df['전체외국인수'].replace({0:np.nan})
df['short_pct'] = df['단기외국인수'] / df['전체외국인수'].replace({0:np.nan})
df[['long_pct','short_pct']] = df[['long_pct','short_pct']].fillna(0)

# 100% stacked bar (short vs long) for all districts
labels = df['자치구'].tolist()
longs = df['long_pct'].tolist()
shorts = df['short_pct'].tolist()

plt.figure(figsize=(14,6))
bar1 = plt.bar(labels, longs, label='장기', color='#4C72B0')
bar2 = plt.bar(labels, shorts, bottom=longs, label='단기', color='#DD8452')
plt.xticks(rotation=45, ha='right')
plt.ylabel('비율 (장기/단기 합 = 1.0)')
plt.title('자치구별 장기 vs 단기 외국인 비율 (부분비율)')
plt.legend()
plt.tight_layout()
out_stack = os.path.join(AI_RESULTS, 'foreigners_short_long_stacked.png')
plt.savefig(out_stack, dpi=150)
plt.close()
print('Saved stacked bar ->', out_stack)

# Top-10 by 외국인비율(%)
top10 = df.sort_values('외국인비율(%)', ascending=False).head(10)
cols = ['자치구','장기외국인수','단기외국인수','전체외국인수','지역인구','외국인비율(%)','long_pct','short_pct']
top10[cols].to_csv(os.path.join(AI_RESULTS, 'foreigners_top10_short_long.csv'), index=False, encoding='utf-8-sig')
print('Saved top-10 CSV ->', os.path.join(AI_RESULTS, 'foreigners_top10_short_long.csv'))

# Also save numeric counts for all districts
df[cols].to_csv(os.path.join(AI_RESULTS, 'foreigners_short_long_counts.csv'), index=False, encoding='utf-8-sig')
print('Saved counts CSV ->', os.path.join(AI_RESULTS, 'foreigners_short_long_counts.csv'))

print('\nDone additional analysis. Files in', AI_RESULTS)
