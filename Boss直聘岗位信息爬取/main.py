# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
#
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")  # 注意这里不再自启动chrome实例，而是直接接管现有端口
#
# # 指向你的chromedriver.exe
# service = Service(executable_path=r"D:\appdata\chromedriver-win64\chromedriver.exe")
# driver = webdriver.Chrome(service=service, options=chrome_options)
#
#
# salary_eles = driver.find_elements(By.CLASS_NAME, "job-salary")
# decode_map = {
#     '': '3',
#     '': '5',
#     '': '0',
#     '': '7',
#     '': '2',
#     '': '4',
#     '': '1',
#     '': '8',
#     '': '9',
#     '': '6',
#
#     # ...
# }
#
# for ele in salary_eles:
#     raw = ele.text
#     decoded = ''.join(decode_map.get(ch, ch) for ch in raw)
#     print(decoded)

from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# 连接到已打开的Chrome实例
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 指向chromedriver路径
service = Service(executable_path=r"D:\appdata\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# 用于存储爬取的数据
job_data = []

# 等待职位列表容器加载完成
try:
    job_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-list-container"))
    )
    print("成功找到职位列表容器")
except Exception as e:
    print(f"找不到职位列表容器: {str(e)}")
    job_container = driver.find_element(By.TAG_NAME, "body")  # 如果找不到容器，使用body作为备用


# 爬取详情页信息的函数
def get_job_details(job_url):
    original_window = driver.current_window_handle

    # 打开新标签页
    driver.execute_script(f"window.open('{job_url}');")
    time.sleep(2)

    # 切换到新标签页
    new_window = [window for window in driver.window_handles if window != original_window][0]
    driver.switch_to.window(new_window)

    # 等待详情页加载
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-detail"))
        )
        print("详情页加载完成")
    except:
        print("等待详情页加载超时")

    job_details = {}

    try:
        # 尝试获取职位描述
        job_desc_selectors = [".job-sec-text", ".text", ".job-detail-section", "[class*='description']"]
        for selector in job_desc_selectors:
            desc_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if desc_elements:
                job_details["职位描述"] = desc_elements[0].text
                print(f"找到职位描述，长度: {len(job_details['职位描述'])}")
                break

        if "职位描述" not in job_details:
            job_details["职位描述"] = "未找到职位描述"

        # 尝试获取公司信息
        company_info_selectors = [".company-info", ".sider-company", "[class*='company-info']"]
        for selector in company_info_selectors:
            company_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if company_elements:
                job_details["公司详情"] = company_elements[0].text
                print(f"找到公司详情，长度: {len(job_details['公司详情'])}")
                break

        if "公司详情" not in job_details:
            job_details["公司详情"] = "未找到公司详情"

        # 尝试获取HR信息
        hr_info_selectors = [".boss-info", ".user-info", "[class*='recruiter']"]
        for selector in hr_info_selectors:
            hr_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if hr_elements:
                job_details["HR信息"] = hr_elements[0].text
                print(f"找到HR信息: {job_details['HR信息'][:50]}...")
                break

        if "HR信息" not in job_details:
            job_details["HR信息"] = "未找到HR信息"

        # 尝试获取福利标签
        welfare_selectors = [".job-tags", ".job-welfare", "[class*='welfare']", "[class*='tag']"]
        for selector in welfare_selectors:
            welfare_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if welfare_elements:
                job_details["福利标签"] = welfare_elements[0].text
                print(f"找到福利标签: {job_details['福利标签']}")
                break

        if "福利标签" not in job_details:
            job_details["福利标签"] = "未找到福利标签"

    except Exception as e:
        print(f"爬取详情页时出错: {str(e)}")

    # 关闭详情页并切回原页面
    driver.close()
    driver.switch_to.window(original_window)

    return job_details


# 滚动和爬取数据的函数
def scroll_and_scrape(max_jobs=5):
    jobs_scraped = 0
    page_num = 1

    # 使用已知有效的选择器
    job_items_selector = "li[class*='job']"

    while jobs_scraped < max_jobs:
        print(f"\n开始爬取第 {page_num} 页")
        # 获取职位项
        job_items = driver.find_elements(By.CSS_SELECTOR, job_items_selector)
        print(f"当前页找到 {len(job_items)} 个职位项")

        # 如果没有找到职位项，可能需要滚动页面
        if not job_items:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
            job_items = driver.find_elements(By.CSS_SELECTOR, job_items_selector)
            print(f"滚动后找到 {len(job_items)} 个职位项")

        for idx, job_item in enumerate(job_items):
            if jobs_scraped >= max_jobs:
                break

            try:
                print(f"\n处理第 {idx + 1} 个职位项:")

                # 获取职位名称
                job_name_elements = job_item.find_elements(By.CSS_SELECTOR, ".job-name")
                job_name = job_name_elements[0].text if job_name_elements else "未找到职位名称"
                print(f"职位名称: {job_name}")

                # 获取详情页链接
                job_link = None
                if job_name_elements:
                    job_link = job_name_elements[0].get_attribute("href")

                if not job_link:
                    link_elements = job_item.find_elements(By.CSS_SELECTOR, "a")
                    for link in link_elements:
                        href = link.get_attribute("href")
                        if href and "job_detail" in href:
                            job_link = href
                            break

                # 获取薪资
                salary_elements = job_item.find_elements(By.CSS_SELECTOR, ".job-salary")
                salary = salary_elements[0].text if salary_elements else "未找到薪资"
                print(f"薪资: {salary}")

                # 获取公司名称和地点
                boss_elements = job_item.find_elements(By.CSS_SELECTOR, ".boss-name")
                company = boss_elements[0].text if boss_elements else "未找到公司名称"

                location_elements = job_item.find_elements(By.CSS_SELECTOR, ".company-location")
                location = location_elements[0].text if location_elements else "未找到工作地点"

                # 获取经验和学历要求
                tag_elements = job_item.find_elements(By.CSS_SELECTOR, ".tag-list li")
                experience = tag_elements[0].text if len(tag_elements) > 0 else "未知"
                education = tag_elements[1].text if len(tag_elements) > 1 else "未知"

                job_info = {
                    "职位名称": job_name,
                    "薪资范围": salary,
                    "公司名称": company,
                    "工作地点": location,
                    "经验要求": experience,
                    "学历要求": education
                }

                # 如果有详情页链接，爬取详情页
                if job_link:
                    print(f"找到详情页链接: {job_link}")
                    job_details = get_job_details(job_link)
                    print(job_details)
                    # 合并列表页和详情页的数据
                    job_info.update(job_details)
                else:
                    print("未找到详情页链接")
                    job_info.update({
                        "职位描述": "未找到详情页链接",
                        "公司详情": "未找到详情页链接",
                        "HR信息": "未找到详情页链接",
                        "福利标签": "未找到详情页链接"
                    })

                # 将数据添加到列表
                job_data.append(job_info)

                jobs_scraped += 1
                print(f"已爬取 {jobs_scraped}/{max_jobs} 个职位")

            except Exception as e:
                print(f"爬取职位信息时出错: {str(e)}")

        if jobs_scraped >= max_jobs:
            break

        # 尝试点击下一页按钮
        try:
            next_page_selectors = [".next", ".page-next", "[ka^='page-next']", "a:contains('下一页')",
                                   ".page-next:not(.disabled)"]
            next_page_clicked = False

            for selector in next_page_selectors:
                try:
                    next_page_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if next_page_elements and "disabled" not in next_page_elements[0].get_attribute("class"):
                        print(f"尝试点击下一页按钮: {selector}")
                        next_page_elements[0].click()
                        time.sleep(3)  # 等待新页面加载
                        next_page_clicked = True
                        break
                except:
                    continue

            if next_page_clicked:
                page_num += 1
                print(f"成功翻到第 {page_num} 页")
            else:
                print("未找到下一页按钮或已到最后一页")
                break

        except Exception as e:
            print(f"翻页时出错: {str(e)}")
            break


# 执行爬取
try:
    # 确保已经打开了Boss直聘的搜索页面
    scroll_and_scrape(max_jobs=5)  # 设置小一点的数量进行测试，因为详情页爬取会花更多时间

    # 将数据保存到Excel
    if job_data:
        df = pd.DataFrame(job_data)
        df.to_excel("boss_python_jobs_with_details.xlsx", index=False)
        print(f"爬取完成，共获取了 {len(job_data)} 条数据，已保存到Excel文件中")
    else:
        print("未获取到任何数据，请检查页面结构和选择器")

except Exception as e:
    print(f"爬取过程中出错: {str(e)}")

