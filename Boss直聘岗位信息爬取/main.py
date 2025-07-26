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

# 连接到已打开的Chrome实例
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 指向chromedriver路径
service = Service(executable_path=r"D:\appdata\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=chrome_options)

# 用于存储爬取的数据
job_data = []

decode_map = {
    '': '3',
    '': '5',
    '': '0',
    '': '7',
    '': '2',
    '': '4',
    '': '1',
    '': '8',
    '': '9',
    '': '6',
}

print(f"当前页面: {driver.title}")

# 等待页面加载完毕
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='job']"))
)

# 获取职位列表
job_items = driver.find_elements(By.CSS_SELECTOR, "li[class*='job']")
print(f"找到 {len(job_items)} 个职位")

# 爬取前5个职位的信息
max_jobs = 300
for idx, job_item in enumerate(job_items[:max_jobs]):
    try:
        print(f"\n爬取第 {idx + 1} 个职位:")

        # 获取简略信息
        job_name = job_item.find_element(By.CSS_SELECTOR, ".job-name").text
        salary = job_item.find_element(By.CSS_SELECTOR, ".job-salary").text
        salary = ''.join(decode_map.get(ch, ch) for ch in salary)
        # 获取标签信息（经验和学历）
        tag_elements = job_item.find_elements(By.CSS_SELECTOR, ".tag-list li")
        experience = tag_elements[0].text if len(tag_elements) > 0 else "未知"
        education = tag_elements[1].text if len(tag_elements) > 1 else "未知"

        # 获取公司和地点信息
        company = job_item.find_element(By.CSS_SELECTOR, ".boss-name").text
        location = job_item.find_element(By.CSS_SELECTOR, ".company-location").text

        print(f"职位名称: {job_name}")
        print(f"薪资: {salary}")
        print(f"经验要求: {experience}")
        print(f"学历要求: {education}")
        print(f"公司名称: {company}")
        print(f"工作地点: {location}")

        # 确保元素可见
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_item)
        time.sleep(1)

        # 点击职位名称进入详情页
        job_name_element = job_item.find_element(By.CSS_SELECTOR, ".job-name")
        driver.execute_script("arguments[0].click();", job_name_element)

        # 等待详情页加载
        time.sleep(10)

        # 爬取详情页信息
        try:
            # 获取职位描述
            job_desc = driver.find_element(By.CSS_SELECTOR, ".desc").text
            print(f"职位描述: {job_desc[:100]}...")

            # 获取HR信息
            hr_name = driver.find_element(By.CSS_SELECTOR, ".name").text.split()[0]
            print(f"HR: {hr_name}")

            # 获取HR信息（公司和职位）
            hr_info = driver.find_element(By.CSS_SELECTOR, ".boss-info-attr").text
            print(f"HR信息: {hr_info}")
        except Exception as e:
            print(f"获取详情信息出错: {str(e)}")
            job_desc = "未找到"
            hr_name = "未找到"
            hr_info = "未找到"

        # 保存数据
        job_data.append({
            "职位名称": job_name,
            "薪资范围": salary,
            "经验要求": experience,
            "学历要求": education,
            "公司名称": company,
            "工作地点": location,
            "职位描述": job_desc,
            "HR姓名": hr_name,
            "HR信息": hr_info
        })

        # 返回列表页
        time.sleep(2)

        # 重新获取职位列表（因为页面刷新了）
        job_items = driver.find_elements(By.CSS_SELECTOR, "li[class*='job']")

    except Exception as e:
        print(f"处理职位时出错: {str(e)}")

# 将数据保存到Excel
if job_data:
    df = pd.DataFrame(job_data)
    df.to_excel("boss_python_jobs.xlsx", index=False)
    print(f"爬取完成，共获取了 {len(job_data)} 条数据，已保存到Excel文件中")
else:
    print("未获取到任何数据")



