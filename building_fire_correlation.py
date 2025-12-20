
import pandas as pd

# Load the datasets
building_df = pd.read_csv('filtered_data/building_year_by_gu.csv')
fire_rate_df = pd.read_csv('filtered_data/구별_만명당_화재율.csv')

# Rename columns for merging
fire_rate_df.rename(columns={'자치구': '구'}, inplace=True)

# Merge the dataframes
merged_df = pd.merge(building_df, fire_rate_df, on='구')

# Calculate the correlation
correlation = merged_df[['1989년이전비율(%)', '화재율(1만명당)']].corr()

# Print the correlation matrix
print("Correlation between 'Old Building Ratio' and 'Fire Rate per 10k People':")
print(correlation)

# Save the correlation matrix to a file
correlation.to_csv('results/building_fire_correlation.csv')

# Visualize the relationship
import matplotlib.pyplot as plt
import seaborn as sns

plt.rc('font', family='Malgun Gothic')
plt.figure(figsize=(10, 6))
sns.scatterplot(data=merged_df, x='1989년이전비율(%)', y='화재율(1만명당)', hue='구', s=100)
plt.title('Correlation between Old Building Ratio and Fire Rate')
plt.xlabel('Old Building Ratio (%)')
plt.ylabel('Fire Rate (per 10k people)')
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.tight_layout()
plt.savefig('results/building_fire_correlation.png')

print("\nScatter plot saved to 'results/building_fire_correlation.png'")
