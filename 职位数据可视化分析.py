import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
from datetime import datetime
import numpy as np
from matplotlib.font_manager import FontProperties

# 设置中文字体
try:
    # 尝试使用微软雅黑字体
    font = FontProperties(fname=r'C:\Windows\Fonts\msyh.ttc')
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except:
    print("警告：找不到微软雅黑字体，图表中文可能无法正常显示")
    # 尝试使用其他可能存在的中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'SimSun', 'Arial Unicode MS']

# 设置图表风格
sns.set(style="whitegrid")
plt.style.use('ggplot')

# 定义文件路径
csv_file_path = None

# 查找当前目录下的CSV文件
for file in os.listdir():
    if file.startswith("1010兼职网职位信息") and file.endswith(".csv"):
        csv_file_path = file
        break

if csv_file_path is None:
    print("错误：找不到1010兼职网职位信息的CSV文件！")
    exit(1)

print(f"正在分析文件: {csv_file_path}")

# 读取CSV文件
try:
    df = pd.read_csv(csv_file_path)
    print(f"成功读取数据，共有{len(df)}条职位信息")
except Exception as e:
    print(f"读取CSV文件时出错: {str(e)}")
    exit(1)

# 数据预处理
def preprocess_data(df):
    # 复制数据框以避免修改原始数据
    df_processed = df.copy()
    
    # 将薪资转换为数值型
    df_processed['薪资'] = pd.to_numeric(df_processed['薪资'], errors='coerce')
    
    # 处理缺失值
    print(f"处理前数据行数: {len(df_processed)}")
    df_processed = df_processed.dropna(subset=['薪资'])
    print(f"处理后数据行数: {len(df_processed)}")
    
    # 标准化发布时间格式
    def standardize_date(date_str):
        if pd.isna(date_str):
            return None
        # 假设格式为MM-DD
        match = re.search(r'(\d{2})-(\d{2})', str(date_str))
        if match:
            month, day = match.groups()
            # 使用当前年份
            current_year = datetime.now().year
            return f"{current_year}-{month}-{day}"
        return None
    
    df_processed['标准发布时间'] = df_processed['发布时间'].apply(standardize_date)
    df_processed['标准发布时间'] = pd.to_datetime(df_processed['标准发布时间'], errors='coerce')
    
    return df_processed

# 预处理数据
df_processed = preprocess_data(df)

# 创建结果目录
results_dir = "可视化分析结果"
os.makedirs(results_dir, exist_ok=True)

# 1. 薪资分布分析
def analyze_salary(df):
    print("\n===== 薪资分布分析 =====")
    
    # 按薪资单位分组计算统计信息
    salary_stats = df.groupby('薪资单位')['薪资'].agg(['count', 'mean', 'median', 'min', 'max']).reset_index()
    print("\n薪资统计信息:")
    print(salary_stats)
    
    # 绘制不同薪资单位的薪资分布
    plt.figure(figsize=(12, 8))
    
    # 获取唯一的薪资单位
    unique_units = df['薪资单位'].unique()
    
    # 为每个薪资单位创建子图
    for i, unit in enumerate(unique_units, 1):
        if pd.isna(unit) or unit == "":
            continue
            
        unit_data = df[df['薪资单位'] == unit]
        
        # 跳过数据量太少的单位
        if len(unit_data) < 5:
            continue
            
        plt.subplot(len(unique_units), 1, i)
        
        # 使用直方图和核密度估计
        sns.histplot(unit_data['薪资'], kde=True, bins=20)
        plt.title(f'薪资分布 - {unit}', fontproperties=font)
        plt.xlabel('薪资', fontproperties=font)
        plt.ylabel('频数', fontproperties=font)
        
        # 添加均值和中位数线
        plt.axvline(unit_data['薪资'].mean(), color='r', linestyle='--', label=f'均值: {unit_data["薪资"].mean():.2f}')
        plt.axvline(unit_data['薪资'].median(), color='g', linestyle='-.', label=f'中位数: {unit_data["薪资"].median():.2f}')
        plt.legend(prop=font)
    
    plt.tight_layout()
    plt.savefig(f"{results_dir}/薪资分布.png", dpi=300)
    plt.close()
    
    # 绘制薪资单位分布饼图
    plt.figure(figsize=(10, 8))
    unit_counts = df['薪资单位'].value_counts()
    plt.pie(unit_counts, labels=unit_counts.index, autopct='%1.1f%%', startangle=90, shadow=True)
    plt.title('薪资单位分布', fontproperties=font, fontsize=16)
    plt.axis('equal')  # 保持饼图为圆形
    plt.savefig(f"{results_dir}/薪资单位分布.png", dpi=300)
    plt.close()
    
    # 绘制箱线图比较不同薪资单位的分布
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='薪资单位', y='薪资', data=df)
    plt.title('不同薪资单位的薪资分布', fontproperties=font, fontsize=16)
    plt.xlabel('薪资单位', fontproperties=font, fontsize=14)
    plt.ylabel('薪资', fontproperties=font, fontsize=14)
    plt.xticks(rotation=45)
    plt.savefig(f"{results_dir}/薪资箱线图.png", dpi=300)
    plt.close()

# 2. 结算方式分析
def analyze_payment_type(df):
    print("\n===== 结算方式分析 =====")
    
    # 统计不同结算方式的数量
    payment_counts = df['结算方式'].value_counts()
    print("\n结算方式统计:")
    print(payment_counts)
    
    # 绘制结算方式分布饼图
    plt.figure(figsize=(10, 8))
    plt.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%', startangle=90, shadow=True)
    plt.title('结算方式分布', fontproperties=font, fontsize=16)
    plt.axis('equal')  # 保持饼图为圆形
    plt.savefig(f"{results_dir}/结算方式分布.png", dpi=300)
    plt.close()
    
    # 分析不同结算方式的薪资差异
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='结算方式', y='薪资', data=df)
    plt.title('不同结算方式的薪资分布', fontproperties=font, fontsize=16)
    plt.xlabel('结算方式', fontproperties=font, fontsize=14)
    plt.ylabel('薪资', fontproperties=font, fontsize=14)
    plt.xticks(rotation=45)
    plt.savefig(f"{results_dir}/结算方式薪资对比.png", dpi=300)
    plt.close()
    
    # 结算方式与薪资单位的关系
    plt.figure(figsize=(14, 10))
    payment_unit_counts = df.groupby(['结算方式', '薪资单位']).size().unstack().fillna(0)
    payment_unit_counts.plot(kind='bar', stacked=True)
    plt.title('结算方式与薪资单位的关系', fontproperties=font, fontsize=16)
    plt.xlabel('结算方式', fontproperties=font, fontsize=14)
    plt.ylabel('职位数量', fontproperties=font, fontsize=14)
    plt.legend(title='薪资单位', prop=font)
    plt.xticks(rotation=45)
    plt.savefig(f"{results_dir}/结算方式与薪资单位关系.png", dpi=300)
    plt.close()

# 3. 发布时间分析
def analyze_publish_time(df):
    print("\n===== 发布时间分析 =====")
    
    # 检查是否有有效的日期数据
    if df['标准发布时间'].isna().all():
        print("没有有效的发布时间数据，跳过发布时间分析")
        return
    
    # 按日期统计职位数量
    df['发布日期'] = df['标准发布时间'].dt.date
    daily_counts = df.groupby('发布日期').size()
    
    print("\n每日发布职位数量:")
    print(daily_counts)
    
    # 绘制发布时间趋势图
    plt.figure(figsize=(14, 8))
    daily_counts.plot(kind='line', marker='o')
    plt.title('职位发布时间趋势', fontproperties=font, fontsize=16)
    plt.xlabel('日期', fontproperties=font, fontsize=14)
    plt.ylabel('职位数量', fontproperties=font, fontsize=14)
    plt.grid(True)
    plt.savefig(f"{results_dir}/职位发布时间趋势.png", dpi=300)
    plt.close()
    
    # 按星期几分析发布数量
    df['星期'] = df['标准发布时间'].dt.day_name()
    weekday_counts = df.groupby('星期').size()
    
    # 确保星期几按顺序排列
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_names = {'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三', 'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'}
    
    # 转换英文星期名为中文
    weekday_counts_ordered = pd.Series([weekday_counts.get(day, 0) for day in weekday_order], index=[weekday_names[day] for day in weekday_order])
    
    plt.figure(figsize=(12, 8))
    weekday_counts_ordered.plot(kind='bar')
    plt.title('不同星期的职位发布数量', fontproperties=font, fontsize=16)
    plt.xlabel('星期', fontproperties=font, fontsize=14)
    plt.ylabel('职位数量', fontproperties=font, fontsize=14)
    plt.savefig(f"{results_dir}/星期职位发布数量.png", dpi=300)
    plt.close()

# 4. 公司分析
def analyze_company(df):
    print("\n===== 公司分析 =====")
    
    # 统计发布职位最多的公司
    company_counts = df['公司名称'].value_counts().head(10)
    print("\n发布职位最多的10家公司:")
    print(company_counts)
    
    # 绘制发布职位最多的公司柱状图
    plt.figure(figsize=(14, 8))
    company_counts.plot(kind='bar')
    plt.title('发布职位最多的公司', fontproperties=font, fontsize=16)
    plt.xlabel('公司名称', fontproperties=font, fontsize=14)
    plt.ylabel('职位数量', fontproperties=font, fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{results_dir}/发布职位最多的公司.png", dpi=300)
    plt.close()
    
    # 分析不同公司的薪资水平
    top_companies = company_counts.index.tolist()
    company_salary = df[df['公司名称'].isin(top_companies)].groupby('公司名称')['薪资'].agg(['mean', 'median']).sort_values('mean', ascending=False)
    
    print("\n不同公司的薪资水平:")
    print(company_salary)
    
    # 绘制不同公司的薪资水平对比
    plt.figure(figsize=(14, 8))
    company_salary.plot(kind='bar')
    plt.title('不同公司的薪资水平对比', fontproperties=font, fontsize=16)
    plt.xlabel('公司名称', fontproperties=font, fontsize=14)
    plt.ylabel('薪资', fontproperties=font, fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.legend(prop=font)
    plt.tight_layout()
    plt.savefig(f"{results_dir}/公司薪资水平对比.png", dpi=300)
    plt.close()

# 5. 职位标题关键词分析
def analyze_job_title(df):
    print("\n===== 职位标题关键词分析 =====")
    
    # 提取职位标题中的关键词
    all_titles = ' '.join(df['职位标题'].dropna())
    
    # 定义一些常见的关键词
    keywords = ['日结', '周结', '月结', '全职', '兼职', '临时', '长期', '短期', '扫描', '分拣', '快递', '客服', '销售', '促销', '服务员', '传单', '派发', '礼仪', '模特', '翻译', '教师', '家教', '设计', '文员', '助理', '实习', '会计', '出纳', '司机', '保安', '保洁', '厨师', '送餐', '外卖', '仓库', '搬运', '装卸', '包装', '质检', '操作', '维修', '安装', '电工', '焊工', '木工', '油漆', '美工', '摄影', '主播', '编辑', '策划', '运营', '程序', '开发', '测试', '网络', '电话', '前台', '收银', '导购', '理货', '采购', '跟单', '物流', '仓管', '快递员', '快递分拣', '快递打包', '快递扫描', '快递装卸', '快递理货', '快递仓管', '快递操作', '快递分拣员', '快递打包员', '快递扫描员', '快递装卸工', '快递理货员', '快递仓管员', '快递操作员']
    
    # 统计关键词出现次数
    keyword_counts = {}
    for keyword in keywords:
        count = all_titles.count(keyword)
        if count > 0:
            keyword_counts[keyword] = count
    
    # 按出现次数排序
    keyword_counts = dict(sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True))
    
    print("\n职位标题关键词统计:")
    for keyword, count in list(keyword_counts.items())[:20]:
        print(f"{keyword}: {count}")
    
    # 绘制关键词词云图
    try:
        from wordcloud import WordCloud
        
        # 创建词云
        wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=r'C:\Windows\Fonts\msyh.ttc', max_words=100).generate_from_frequencies(keyword_counts)
        
        # 显示词云图
        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('职位标题关键词词云', fontproperties=font, fontsize=16)
        plt.savefig(f"{results_dir}/职位标题关键词词云.png", dpi=300)
        plt.close()
    except ImportError:
        print("未安装wordcloud库，跳过词云图生成")
        # 使用条形图替代
        plt.figure(figsize=(14, 10))
        top_keywords = dict(list(keyword_counts.items())[:20])
        plt.barh(list(top_keywords.keys()), list(top_keywords.values()))
        plt.title('职位标题热门关键词', fontproperties=font, fontsize=16)
        plt.xlabel('出现次数', fontproperties=font, fontsize=14)
        plt.ylabel('关键词', fontproperties=font, fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{results_dir}/职位标题热门关键词.png", dpi=300)
        plt.close()
    
    # 分析含有特定关键词的职位薪资情况
    top_keywords = list(keyword_counts.keys())[:10]
    
    plt.figure(figsize=(14, 10))
    for i, keyword in enumerate(top_keywords):
        keyword_data = df[df['职位标题'].str.contains(keyword, na=False)]
        if len(keyword_data) > 5:  # 只分析有足够数据的关键词
            plt.subplot(5, 2, i+1)
            sns.boxplot(y=keyword_data['薪资'])
            plt.title(f'{keyword}职位薪资分布', fontproperties=font)
            plt.ylabel('薪资', fontproperties=font)
    
    plt.tight_layout()
    plt.savefig(f"{results_dir}/关键词薪资分布.png", dpi=300)
    plt.close()

# 6. 综合分析报告
def generate_report(df):
    print("\n===== 生成综合分析报告 =====")
    
    # 创建一个HTML报告
    report_file = f"{results_dir}/1010兼职网职位分析报告.html"
    
    # 基本统计信息
    total_jobs = len(df)
    avg_salary = df['薪资'].mean()
    median_salary = df['薪资'].median()
    most_common_payment = df['结算方式'].value_counts().index[0]
    most_common_unit = df['薪资单位'].value_counts().index[0]
    top_company = df['公司名称'].value_counts().index[0]
    
    # 创建HTML内容
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>1010兼职网职位分析报告</title>
        <style>
            body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; text-align: center; }}
            h2 {{ color: #3498db; margin-top: 30px; }}
            .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .chart {{ text-align: center; margin: 30px 0; }}
            .chart img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #3498db; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .footer {{ text-align: center; margin-top: 50px; color: #7f8c8d; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <h1>1010兼职网职位分析报告</h1>
        
        <div class="summary">
            <h2>数据概览</h2>
            <p>分析文件: {csv_file_path}</p>
            <p>总职位数: {total_jobs}</p>
            <p>平均薪资: {avg_salary:.2f}</p>
            <p>薪资中位数: {median_salary:.2f}</p>
            <p>最常见结算方式: {most_common_payment}</p>
            <p>最常见薪资单位: {most_common_unit}</p>
            <p>发布职位最多的公司: {top_company}</p>
        </div>
        
        <h2>薪资分析</h2>
        <div class="chart">
            <img src="薪资分布.png" alt="薪资分布">
            <p>不同薪资单位的薪资分布情况</p>
        </div>
        
        <div class="chart">
            <img src="薪资单位分布.png" alt="薪资单位分布">
            <p>薪资单位的分布比例</p>
        </div>
        
        <div class="chart">
            <img src="薪资箱线图.png" alt="薪资箱线图">
            <p>不同薪资单位的薪资分布箱线图</p>
        </div>
        
        <h2>结算方式分析</h2>
        <div class="chart">
            <img src="结算方式分布.png" alt="结算方式分布">
            <p>不同结算方式的分布比例</p>
        </div>
        
        <div class="chart">
            <img src="结算方式薪资对比.png" alt="结算方式薪资对比">
            <p>不同结算方式的薪资水平对比</p>
        </div>
        
        <div class="chart">
            <img src="结算方式与薪资单位关系.png" alt="结算方式与薪资单位关系">
            <p>结算方式与薪资单位的关系分析</p>
        </div>
        
        <h2>发布时间分析</h2>
        <div class="chart">
            <img src="职位发布时间趋势.png" alt="职位发布时间趋势">
            <p>职位发布的时间趋势</p>
        </div>
        
        <div class="chart">
            <img src="星期职位发布数量.png" alt="星期职位发布数量">
            <p>不同星期的职位发布数量</p>
        </div>
        
        <h2>公司分析</h2>
        <div class="chart">
            <img src="发布职位最多的公司.png" alt="发布职位最多的公司">
            <p>发布职位数量最多的公司</p>
        </div>
        
        <div class="chart">
            <img src="公司薪资水平对比.png" alt="公司薪资水平对比">
            <p>不同公司的薪资水平对比</p>
        </div>
        
        <h2>职位关键词分析</h2>
        <div class="chart">
            <img src="职位标题关键词词云.png" alt="职位标题关键词词云" onerror="this.src='职位标题热门关键词.png';this.onerror=null;">
            <p>职位标题中的热门关键词</p>
        </div>
        
        <div class="chart">
            <img src="关键词薪资分布.png" alt="关键词薪资分布">
            <p>不同关键词职位的薪资分布</p>
        </div>
        
        <div class="footer">
            <p>分析生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>本报告由Python自动生成</p>
        </div>
    </body>
    </html>
    """
    
    # 保存HTML报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n综合分析报告已生成: {report_file}")

# 主函数
def main():
    print("===== 1010兼职网职位信息数据分析 =====")
    print(f"分析开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行各项分析
    analyze_salary(df_processed)
    analyze_payment_type(df_processed)
    analyze_publish_time(df_processed)
    analyze_company(df_processed)
    analyze_job_title(df_processed)
    
    # 生成综合报告
    generate_report(df_processed)
    
    print(f"\n分析结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"分析结果已保存到目录: {os.path.abspath(results_dir)}")
    print("\n请打开生成的HTML报告查看完整分析结果")

# 执行主函数
if __name__ == "__main__":
    main()