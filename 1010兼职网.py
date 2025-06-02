from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re
import json
import csv
import os
from datetime import datetime

# 创建一个列表来存储所有职位信息
job_list = []

# 设置Edge浏览器选项
edge_options = Options()
# 如果需要无头模式（不显示浏览器界面），取消下面这行的注释
# edge_options.add_argument('--headless')

# 添加一些额外的选项，使爬虫更稳定
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--no-sandbox')
edge_options.add_argument('--disable-dev-shm-usage')
edge_options.add_argument('--disable-extensions')

# 初始化Edge浏览器
print("正在启动Edge浏览器...")
try:
    driver = webdriver.Edge(options=edge_options)
    print("Edge浏览器启动成功！")
except Exception as e:
    print(f"启动Edge浏览器失败: {str(e)}")
    print("请确保已安装Microsoft Edge浏览器和对应版本的WebDriver")
    exit(1)

# 设置等待时间
wait = WebDriverWait(driver, 10)

# 定义一个函数来获取职位详情
def get_job_details(job_url):
    print(f"正在获取职位详情: {job_url}")
    # 打开职位详情页面
    try:
        driver.execute_script(f"window.open('{job_url}', '_blank');")
        # 切换到新打开的标签页
        driver.switch_to.window(driver.window_handles[1])
        
        try:
            # 等待职位详情加载完成
            job_detail_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/span[4]/div[2]')))
            job_detail = job_detail_element.text
        except (TimeoutException, NoSuchElementException) as e:
            print(f"获取职位详情失败: {str(e)}")
            job_detail = "无法获取职位详情"
        
        # 关闭当前标签页并切回主页面
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        return job_detail
    except Exception as e:
        print(f"打开职位详情页面失败: {str(e)}")
        # 确保切回主页面
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return "获取职位详情时出错"

# 定义一个函数来处理每个页面的职位列表
def process_page(page_url):
    print(f"\n正在处理页面: {page_url}")
    try:
        driver.get(page_url)
        
        # 等待职位列表加载完成
        try:
            job_list_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/ul[1]')))
            
            # 获取所有职位列表项
            job_items = job_list_element.find_elements(By.TAG_NAME, 'li')
            print(f"找到 {len(job_items)} 个职位列表项")
            
            for index, job_item in enumerate(job_items, 1):
                try:
                    # 提取职位标题和链接
                    job_title_element = job_item.find_element(By.CSS_SELECTOR, 'span.jobtitle a')
                    job_title = job_title_element.text
                    job_url = job_title_element.get_attribute('href')
                    
                    # 提取薪资
                    try:
                        price_element = job_item.find_element(By.CSS_SELECTOR, 'span.price')
                        price_text = price_element.text
                        # 使用正则表达式提取数字和单位
                        price_match = re.search(r'(\d+)\s*元/(\w+)', price_text)
                        if price_match:
                            price = price_match.group(1)
                            price_unit = price_match.group(2)
                        else:
                            price = price_text
                            price_unit = ""
                    except NoSuchElementException:
                        price = "未提供"
                        price_unit = ""
                    
                    # 提取结算方式
                    try:
                        payment_type = job_item.find_element(By.CSS_SELECTOR, 'span.payment_type').text
                    except NoSuchElementException:
                        payment_type = "未提供"
                    
                    # 提取公司名称
                    try:
                        company = job_item.find_element(By.CSS_SELECTOR, 'span.listcompany a').text
                    except NoSuchElementException:
                        company = "未提供"
                    
                    # 提取发布时间
                    try:
                        publish_time = job_item.find_element(By.CSS_SELECTOR, 'span.listzptime').text.strip()
                    except NoSuchElementException:
                        publish_time = "未提供"
                    
                    print(f"正在处理第 {index} 个职位: {job_title}")
                    
                    # 获取职位详情
                    job_detail = get_job_details(job_url)
                    
                    # 创建职位信息字典
                    job_info = {
                        '职位标题': job_title,
                        '薪资': price,
                        '薪资单位': price_unit,
                        '结算方式': payment_type,
                        '公司名称': company,
                        '发布时间': publish_time,
                        '职位详情': job_detail,
                        '职位链接': job_url
                    }
                    
                    # 将职位信息添加到列表
                    job_list.append(job_info)
                    print(f"已添加职位: {job_title}")
                    
                except Exception as e:
                    print(f"处理职位时出错: {str(e)}")
        
        except (TimeoutException, NoSuchElementException) as e:
            print(f"找不到职位列表元素: {str(e)}")
    
    except Exception as e:
        print(f"处理页面时出错: {str(e)}")

# 保存职位信息到JSON文件
def save_to_json(job_list, filename=None):
    if not filename:
        # 使用当前时间创建文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"1010兼职网职位信息_{timestamp}.json"
    
    # 确保文件名有.json后缀
    if not filename.endswith('.json'):
        filename += '.json'
    
    # 保存为JSON文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(job_list, f, ensure_ascii=False, indent=4)
    
    print(f"\n职位信息已保存到文件: {filename}")
    return filename

# 保存职位信息到CSV文件
def save_to_csv(job_list, filename=None):
    if not filename:
        # 使用当前时间创建文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"1010兼职网职位信息_{timestamp}.csv"
    
    # 确保文件名有.csv后缀
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    # 定义CSV文件的表头
    fieldnames = ['职位标题', '薪资', '薪资单位', '结算方式', '公司名称', '发布时间', '职位详情', '职位链接']
    
    # 保存为CSV文件
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(job_list)
    
    print(f"\n职位信息已保存到CSV文件: {filename}")
    return filename

# 主函数
def main():
    try:
        # 设置起始页和结束页
        start_page = 1
        end_page = 5  # 可以根据需要修改爬取的页数
        
        print(f"\n开始爬取1010兼职网，从第{start_page}页到第{end_page}页")
        
        # 循环处理每一页
        for page_num in range(start_page, end_page + 1):
            page_url = f"https://sz.1010jz.com/job/index{page_num}.html"
            process_page(page_url)
            
            # 每处理完一页，保存一次数据，防止中途出错导致数据丢失
            if job_list:
                temp_filename = f"1010兼职网职位信息_临时保存_第{page_num}页.json"
                save_to_json(job_list, temp_filename)
                temp_csv_filename = f"1010兼职网职位信息_临时保存_第{page_num}页.csv"
                save_to_csv(job_list, temp_csv_filename)
            
            # 添加随机延迟，避免请求过于频繁
            delay = 2 + (page_num % 3)  # 2-4秒的随机延迟
            print(f"等待 {delay} 秒后继续...")
            time.sleep(delay)
        
        # 打印爬取的职位数量
        print(f"\n成功爬取 {len(job_list)} 个职位信息")
        
        # 保存最终结果
        if job_list:
            final_json_filename = save_to_json(job_list)
            final_csv_filename = save_to_csv(job_list)
            
            # 删除临时文件
            for page_num in range(start_page, end_page + 1):
                # 删除临时JSON文件
                temp_json_filename = f"1010兼职网职位信息_临时保存_第{page_num}页.json"
                if os.path.exists(temp_json_filename):
                    try:
                        os.remove(temp_json_filename)
                    except:
                        pass
                
                # 删除临时CSV文件
                temp_csv_filename = f"1010兼职网职位信息_临时保存_第{page_num}页.csv"
                if os.path.exists(temp_csv_filename):
                    try:
                        os.remove(temp_csv_filename)
                    except:
                        pass
            
            # 打印部分职位信息作为示例
            print("\n以下是部分爬取的职位信息示例:")
            for i, job in enumerate(job_list[:5], 1):
                print(f"\n职位 {i}:")
                print(f"标题: {job['职位标题']}")
                print(f"薪资: {job['薪资']} {job['薪资单位']}")
                print(f"结算方式: {job['结算方式']}")
                print(f"公司: {job['公司名称']}")
                print(f"发布时间: {job['发布时间']}")
                print(f"详情摘要: {job['职位详情'][:100]}..." if len(job['职位详情']) > 100 else f"详情: {job['职位详情']}")
            
            print(f"\n完整数据已保存到JSON文件: {final_json_filename}")
            print(f"完整数据已保存到CSV文件: {final_csv_filename}")
        else:
            print("未爬取到任何职位信息")
    
    except Exception as e:
        print(f"主程序出错: {str(e)}")
        # 如果出错，尝试保存已爬取的数据
        if job_list:
            error_json_filename = f"1010兼职网职位信息_错误恢复_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_to_json(job_list, error_json_filename)
            error_csv_filename = f"1010兼职网职位信息_错误恢复_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            save_to_csv(job_list, error_csv_filename)
            print(f"已保存已爬取的 {len(job_list)} 个职位信息到JSON文件: {error_json_filename}")
            print(f"已保存已爬取的 {len(job_list)} 个职位信息到CSV文件: {error_csv_filename}")
    
    finally:
        # 关闭浏览器
        try:
            driver.quit()
            print("浏览器已关闭")
        except:
            pass

# 执行主函数
if __name__ == "__main__":
    print("=== 1010兼职网爬虫程序 ===\n")
    print("本程序将爬取1010兼职网上的招聘信息，并保存为JSON和CSV文件")
    print("请确保您的计算机已安装Microsoft Edge浏览器和对应版本的WebDriver")
    print("程序开始运行...\n")
    main()
    print("\n程序运行结束")