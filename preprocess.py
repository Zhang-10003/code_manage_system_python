import re

"""
    该函数实现的功能：cpp文件的预处理
    具体功能：去掉单行、多行注释，去掉所有的空行（包括注释后的空行）
    参数：
        file_path: 输入文件路径
        destination_path: 输出文件路径
"""
def preprocess(file_path, destination_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 去除多行注释 /* ... */
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # 去除单行注释 //
    content = re.sub(r'//.*', '', content)
    # 去除所有空行（包括注释后的空行）
    content = re.sub(r'\n\s*\n', '\n', content)                   # 去除连续的空行
    content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)  # 去除文件开头的空行
    content = re.sub(r'\n\s*$', '', content, flags=re.MULTILINE)  # 去除文件结尾的空行
    content = re.sub(r'\n\s*\n', '\n', content)                   # 确保没有多余的空行

    # 将清理后的代码保存到目标文件
    with open(destination_path, 'w', encoding='utf-8') as file:
        file.write(content)
