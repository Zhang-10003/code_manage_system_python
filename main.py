from flask import Flask, request, jsonify
import preprocess as pre
import checkRepeatRate as check
import json
from openai import OpenAI
from pathlib import Path

app = Flask(__name__)
# 假设的 calc 函数，计算两个对象之间的值
def calc(obj1, obj2):
    # 先获取两个对象传入的文件路径
    file1_path = obj1['file_path']
    file2_path = obj2['file_path']
    print(file1_path)
    # 预处理两个代码文件
    pre.preprocess(file1_path, 'test1')
    pre.preprocess(file2_path, 'test2')

    # 计算test1和test2的相似度
    similarity = check.cosine_sim('test1', 'test2')
    # 保留两位有效数字
    similarity_rounded = round(similarity, 3)
    print(similarity_rounded)

    # 删除两个临时文件
    # 定义要删除的文件路径
    file1_path = Path("test1")
    file2_path = Path("test2")

    # 删除文件
    try:
        file1_path.unlink()  # unlink() 方法用于删除文件
        file2_path.unlink()
        print("文件已成功删除！")
    except FileNotFoundError as e:
        print(f"错误：文件未找到，无法删除。详细信息：{e}")
    except PermissionError as e:
        print(f"错误：没有权限删除文件。详细信息：{e}")
    except Exception as e:
        print(f"发生未知错误：{e}")

    return similarity_rounded

# 查重
@app.route('/checkRepeatRate', methods=['POST'])
def process():
    # 获取传入的 JSON 数据
    data = request.json
    # 获取阈值
    threshold = data.get('threshold', 0.8)
    # 获取对象列表
    objects = data.get('objects', [])
    # 存储结果的字典
    results = []
    # 两两计算对象之间的值
    for i in range(len(objects)):
        for j in range(i + 1, len(objects)):
            obj1 = objects[i]
            obj2 = objects[j]
            # 计算值
            value = calc(obj1, obj2)
            # 如果值大于阈值，则存储结果
            if value > threshold:
                # 将结果格式化为 [name1, name2, percentage] 的形式
                result = [obj1['name'], obj2['name'], f"{value * 100:.1f}%"]
                results.append(result)
    # 返回结果
    return jsonify(results)

# ai对话接口
@app.route('/api/aiChat', methods=['POST'])
def ai_interface():
    try:
        data = request.json
        user_input = data.get("text", "")

        # 初始化OpenAI客户端
        client = OpenAI(
            api_key="sk-BQ3pzHPLzQkJIgDfom0DlwXsN6278JsnI8Ac3UGL7Ol79KMe",
            base_url="https://api.moonshot.cn/v1",
        )

        # 模拟系统提示和回复
        system_prompt = """
        你是月之暗面（Kimi）的智能客服，你负责回答用户提出的各种问题。请参考文档内容回复用户的问题。

        请使用如下 JSON 格式输出你的回复：
        {
            "text": "文字信息"
        }

        注意：
        1. 只能返回 `text` 字段，不能包含 `image` 或 `url` 字段。
        2. `text` 字段中只能包含文字信息。
        """

        # 调用 API 生成回复
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        answer = completion.choices[0].message.content
        return jsonify({"text": answer, "data": "000"})
    except Exception as e:
        app.logger.error(f"Error occurred: {e}")  # 记录错误日志
        return jsonify({"text": "服务器繁忙", "data": "001"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088)