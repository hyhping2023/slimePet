import re

def contains_chinese(text):
    # 使用正则表达式匹配中文字符
    pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(pattern.search(text))

def contains_english(text):
    # 使用正则表达式匹配英文字符
    pattern = re.compile(r'[a-zA-Z]')
    return bool(pattern.search(text))

def language_detect(text):
    flag = 0
    if contains_chinese(text):
        flag += 1
    if contains_english(text):
        flag += 2
    if flag == 1:
        return "中文"
    elif flag == 2:
        return "英文"
    elif flag == 3:
        return "中英混合"
    else:
        return "多语种混合"
    
def prompt_clear(prompt):
    # 清除多余的空格和换行符
    prompt = prompt.replace("*", "")
    prompt = prompt.replace("\"", "")
    prompt = prompt.replace("”", "").replace("“", "")
    prompt = prompt.replace("（", "").replace("）", "")
    prompt = prompt.replace("《", "").replace("》", "")
    prompt = prompt.replace("【", "").replace("】", "")
    prompt = prompt.replace("(", "").replace(")", "")
    prompt = prompt.replace("：", "").replace(":", "")
    return empty_remove(prompt)

def empty_remove(text):
    # 清除多余的空格和换行符
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\t", "")
    text = text.replace(" ", "")
    return text.strip()