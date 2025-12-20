"""
AI/analysis_foreigner.py

Reads existing project CSVs (read-only) and creates analysis outputs in AI/results.
Do NOT modify files outside AI/; only read them.

Outputs:
 - AI/results/ai_foreigner_summary.csv
 - AI/results/foreigners_bar_all.png
 - AI/results/foreigners_vs_fire_scatter.png (if fire data available)

Run: python AI\analysis_foreigner.py
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set(style='whitegrid')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
AI_RESULTS = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(AI_RESULTS, exist_ok=True)

# Paths to read-only inputs (outside AI folder)
filtered_recalc = os.path.join(ROOT, 'filtered_data', 'foreigners_recalculated.csv')
gu_pop = os.path.join(ROOT, 'filtered_data', 'Gu_Populations.csv')
fire_gu = os.path.join(ROOT, 'results', 'gu_build_fire.csv')

print('Reading inputs (read-only):')
print(' -', filtered_recalc)
print(' -', gu_pop)
print(' -', fire_gu)

# 1) Load recalculated foreigners (must exist from prior steps)
if not os.path.exists(filtered_recalc):
    raise FileNotFoundError(f'Missing required file: {filtered_recalc}')

df = pd.read_csv(filtered_recalc, encoding='utf-8-sig')
# Normalize column names if needed
cols = df.columns.str.strip()
df.columns = cols

# Ensure numeric columns
for c in ['장기외국인수','단기외국인수','전체외국인수','지역인구','외국인비율(%)']:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

# Summary statistics
summary = df[['자치구','장기외국인수','단기외국인수','전체외국인수','지역인구','외국인비율(%)']].copy()
summary = summary.sort_values('외국인비율(%)', ascending=False).reset_index(drop=True)
summary.to_csv(os.path.join(AI_RESULTS, 'ai_foreigner_summary.csv'), index=False, encoding='utf-8-sig')
print('Saved summary CSV ->', os.path.join(AI_RESULTS, 'ai_foreigner_summary.csv'))

# 2) Bar plot: foreigner % for all gu
plt.figure(figsize=(14,6))
plt.bar(summary['자치구'], summary['외국인비율(%)'], color='#DD8452')
plt.xticks(rotation=45, ha='right')
plt.ylabel('외국인 비율 (%)')
plt.title('자치구별 외국인 비율 (장기+단기) / (장기+단기+지역인구)')
plt.tight_layout()
out_bar = os.path.join(AI_RESULTS, 'foreigners_bar_all.png')
plt.savefig(out_bar, dpi=150)
plt.close()
print('Saved bar plot ->', out_bar)

# 3) If fire data exists, merge and compute correlation
if os.path.exists(fire_gu):
    fire_df = pd.read_csv(fire_gu, encoding='utf-8-sig', engine='python')
    # try to find a numeric fire count column
    numeric_candidates = [c for c in fire_df.columns if fire_df[c].dtype in [int, float] or fire_df[c].astype(str).str.isnumeric().all()]
    # Common column might be '건수' or '화재수' or 'count'
    fire_col = None
    for c in fire_df.columns:
        if any(k in c for k in ['건수','화재','count','합계']):
            fire_col = c
            break
    if fire_col is None and numeric_candidates:
        fire_col = numeric_candidates[0]

    if fire_col is not None:
        fire_df = fire_df.rename(columns={fire_col: '화재건수'})
        # normalize gu name
        if '자치구' not in fire_df.columns:
            # try common name columns
            for c in fire_df.columns:
                if '구' in c:
                    fire_df = fire_df.rename(columns={c: '자치구'})
                    break
        fire_df['자치구'] = fire_df['자치구'].astype(str)
        merged = pd.merge(summary, fire_df[['자치구','화재건수']], on='자치구', how='left').fillna(0)
        # compute 화재율 per 10k (using 지역인구)
        merged['화재율_per10k'] = merged['화재건수'] / (merged['지역인구'].replace({0:np.nan}) / 10000.0)
        merged['화재율_per10k'] = merged['화재율_per10k'].fillna(0)

        # scatter plot with regression line
        plt.figure(figsize=(8,6))
        sns.regplot(x='외국인비율(%)', y='화재율_per10k', data=merged, scatter_kws={'s':50})
        plt.xlabel('외국인 비율 (%)')
        plt.ylabel('화재율 (건수 per 10k)')
        plt.title('외국인 비율 vs 화재율 (per 10k)')
        plt.tight_layout()
        out_scatter = os.path.join(AI_RESULTS, 'foreigners_vs_fire_scatter.png')
        plt.savefig(out_scatter, dpi=150)
        plt.close()
        print('Saved scatter plot ->', out_scatter)

        # Pearson correlation
        try:
            r, p = stats.pearsonr(merged['외국인비율(%)'], merged['화재율_per10k'])
        except Exception:
            r, p = (np.nan, np.nan)
        corr_summary = pd.DataFrame([{
            'pearson_r': r,
            'p_value': p
        }])
        corr_summary.to_csv(os.path.join(AI_RESULTS, 'foreigners_fire_correlation.csv'), index=False, encoding='utf-8-sig')
        print('Saved correlation summary ->', os.path.join(AI_RESULTS, 'foreigners_fire_correlation.csv'))
    else:
        print('No suitable fire count column found in', fire_gu)
else:
    print('Fire data not found at', fire_gu, '-- skipping fire correlation analysis')

print('\nDone. Outputs saved in', AI_RESULTS)
