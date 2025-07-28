# 使用Deepseek分析岗位信息
# 目前只是能用，分类效果一般，提示词待优化
import os
import pandas as pd
from openai import OpenAI
import json
# 从系统环境变量中获取API密钥（请自行提前设置好）
# PS C:\WINDOWS\system32> [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-你的密钥", "Machine")
# PS C:\WINDOWS\system32> [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-你的密钥", "User")
api_key = os.environ.get("DEEPSEEK_API_KEY")

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)
deal_result = []
# 获取用户输入的问题
excel_path = r'C:\Users\13989\Desktop\岗位分析.xlsx'  # 你的Excel文件路径
df = pd.read_excel(excel_path)
for index, row in df.iterrows():
    job_description = row['职位描述']  # 获取每行的岗位描述
    question = (f"请你针对岗位的描述以及相关信息，进行分析:{job_description}。"
                "首先判断岗位分类（爬虫、教育、算法、测试、外包、python开发、硬件开发、非python开发，外包很特殊，就是很全那种也算是外包，其他的你自行判断，看看赋予什么样的分类合适）"
                "然后判断岗位福利待遇有哪些，如果是996或者单休这种负福利也请标注出来。"
                "然后就是岗位技术需求，这儿一定要具体，比如需要的语言是什么，框架是什么等等其他数据库、版本控制啥的。"
                "返回的格式请按照格式返回")
    # 调用大模型 API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手，请严格按照下面的 JSON 模式输出结果，直接输出结果，不要额外添加文字。"
                                          "EXAMPLE OUTPUT FORMAT:"
                                          "{岗位分类: ,岗位福利: ,岗位技术需求: }"},
            {"role": "user", "content": question},],
        stream=False)
    # 提取回答内容
    try:
        answer = response.choices[0].message.content
        content = json.loads(answer)
        row['岗位分类']=content['岗位分类']
        row['福利']=content['岗位福利']
        row['技术需求']=content['岗位技术需求']
        deal_result.append(row)
    except:
        deal_result.append(row)
    print(content)
import pandas as pd
df = pd.DataFrame(deal_result)
df.to_excel("分析结果.xlsx", index=False)