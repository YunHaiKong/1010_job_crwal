import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
import seaborn as sns

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('1010兼职网职位信息_20250506_170502.csv')

# 数据清洗：处理薪资列，将无法转换的值设为缺失值
df['薪资'] = pd.to_numeric(df['薪资'], errors='coerce')
df = df.dropna(subset=['薪资'])

# 绘制不同结算方式下平均薪资的柱状图
average_salary = df.groupby('结算方式')['薪资'].mean().round(2).reset_index()
plt.figure(figsize=(10, 6))
plt.bar(average_salary['结算方式'], average_salary['薪资'])
plt.xlabel('结算方式')
plt.ylabel('平均薪资')
plt.title('不同结算方式下的平均薪资')
for i, v in enumerate(average_salary['薪资']):
    plt.text(i, v, str(v), ha='center', va='bottom')
plt.savefig('salary_by_settlement_method.png')
plt.show()

# 绘制不同结算方式下薪资分布的箱线图
plt.figure(figsize=(12, 8))
sns.boxplot(x='结算方式', y='薪资', data=df)
plt.xlabel('结算方式')
plt.ylabel('薪资')
plt.title('不同结算方式下的薪资分布')
plt.savefig('salary_distribution_by_settlement_method.png')
plt.show()

# 生成职位词云图
# 提取职位标题并拼接成文本
job_titles = " ".join(df['职位标题'])
# 中文分词
words = jieba.lcut(job_titles)
word_text = " ".join(words)

# 方案二：正确指定字体路径（以 Windows 为例）
font_path = 'C:/Windows/Fonts/simhei.ttf' # Ensure this font path is correct for the execution environment
wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(word_text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('职位词云图')
# 保存词云图
wordcloud.to_file('job_title_wordcloud.png')
plt.show()

# 绘制不同城市职位数量的条形图
if '城市' in df.columns:
    city_counts = df['城市'].value_counts().reset_index()
    city_counts.columns = ['城市', '职位数量']
    # 选择职位数量最多的前N个城市进行展示，例如前15个
    top_n_cities = 15
    city_counts_top_n = city_counts.head(top_n_cities)

    plt.figure(figsize=(14, 8)) # Increased figure size for better readability
    plt.bar(city_counts_top_n['城市'], city_counts_top_n['职位数量'], color='skyblue')
    plt.xlabel('城市', fontsize=12)
    plt.ylabel('职位数量', fontsize=12)
    plt.title(f'职位数量排名前 {top_n_cities} 的城市分布', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10) # Rotate labels and adjust font
    for i, v_count in enumerate(city_counts_top_n['职位数量']): # Renamed v to v_count
        # Adjust text position slightly above the bar
        plt.text(i, v_count + (city_counts_top_n['职位数量'].max() * 0.01), str(v_count), ha='center', va='bottom', fontsize=9)
    plt.tight_layout() # Adjust layout to prevent labels from overlapping
    plt.savefig('jobs_by_city.png')
    plt.show()
else:
    print("数据中未找到 '城市' 列，无法生成城市职位分布图。")

# 绘制不同薪资单位下薪资分布的箱线图
if '薪资单位' in df.columns:
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='薪资单位', y='薪资', data=df)
    plt.xlabel('薪资单位', fontsize=12)
    plt.ylabel('薪资', fontsize=12)
    plt.title('不同薪资单位下的薪资分布', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()
    plt.savefig('salary_distribution_by_unit.png')
    plt.show()
else:
    print("数据中未找到 '薪资单位' 列，无法生成薪资单位分布图。")

# 分析每日职位发布数量
if '发布时间' in df.columns:
    import re
    from datetime import datetime

    def standardize_date(date_str):
        if pd.isna(date_str):
            return None
        match = re.search(r'(\d{2})-(\d{2})', str(date_str)) # 假设格式为MM-DD
        if match:
            month, day = match.groups()
            current_year = datetime.now().year
            return f"{current_year}-{month}-{day}"
        # 尝试匹配 YYYY-MM-DD 或 YYYY/MM/DD
        match_ymd = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', str(date_str))
        if match_ymd:
            return date_str # Already in a good format or close enough for pd.to_datetime
        return None

    df['标准发布时间'] = df['发布时间'].apply(standardize_date)
    df['标准发布时间'] = pd.to_datetime(df['标准发布时间'], errors='coerce')
    df_time_analysis = df.dropna(subset=['标准发布时间'])

    if not df_time_analysis.empty:
        df_time_analysis['发布日期'] = df_time_analysis['标准发布时间'].dt.date
        daily_counts = df_time_analysis.groupby('发布日期').size().reset_index(name='职位数量')
        daily_counts = daily_counts.sort_values(by='发布日期')

        plt.figure(figsize=(15, 7))
        plt.plot(daily_counts['发布日期'], daily_counts['职位数量'], marker='o', linestyle='-')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('职位数量', fontsize=12)
        plt.title('每日职位发布数量趋势', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('daily_job_postings_trend.png')
        plt.show()
    else:
        print("处理后的发布时间数据为空，无法生成每日职位发布数量趋势图。")
else:
    print("数据中未找到 '发布时间' 列，无法生成每日职位发布数量趋势图。")





