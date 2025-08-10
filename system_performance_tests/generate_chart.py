import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

num_metrics = 14
metric_data = {}

combined_data = pd.DataFrame()

for i in range(1, num_metrics + 1):
    # if you want to also include m10 & m1, comment line 12 & 13
    if i not in [10, 11]:
        continue
    file_name = f"m{i}.csv"
    metric_df = pd.read_csv(file_name, header=None, sep=';', decimal=',')
    combined_data[f'm{i}'] = metric_df.iloc[:, 0]

plt.figure(figsize=(30, 20))
sns.boxplot(data=combined_data, palette="Set2")

plt.title('Metric Computation Times (excluding m10 & m11)')
plt.xlabel('Metrics')
plt.ylabel('Computation Time (s)')

plt.show()
