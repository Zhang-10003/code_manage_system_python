from flask import Flask, request, jsonify
import preprocess as pre
import checkRepeatRate as check
import json
from openai import OpenAI
from pathlib import Path
import mysql.connector
from mysql.connector import Error  #pip install mysql-connector-python


app = Flask(__name__)
# 假设的 calc 函数，计算两个对象之间的值



def calc(obj1, obj2):
    # 先获取两个对象传入的文件路径
    file1_path = obj1['file_path']
    file2_path = obj2['file_path']
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
def ai_interface_chat():
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

        # 解析Kimi的回答
        answer_json = json.loads(answer)
        text_content = answer_json.get("text", "")

        # 判断回答内容是否为代码
        if "#include" in text_content or "using namespace" in text_content or "int main()" in text_content:
            return jsonify({
                "data": "000",
                "text": text_content
            })
        else:
            return jsonify({
                "data": "000",
                "text": text_content
            })

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")  # 记录错误日志
        return jsonify({
            "data": "001",
            "text": "服务器繁忙，请稍后重试"
        }), 500


# ai一键分析代码
@app.route('/api/aiAnalyzeCode', methods=['POST'])
def ai_interface_analyze_code():
    try:
        data = request.json
        user_code_path = data.get("file_path", "")  # 获取用户上传的代码文件路径

        # 从文件中读取代码内容到变量 user_code
        with open(user_code_path, "r", encoding="utf-8") as file:
            user_code = file.read()

        # 初始化OpenAI客户端
        client = OpenAI(
            api_key="sk-BQ3pzHPLzQkJIgDfom0DlwXsN6278JsnI8Ac3UGL7Ol79KMe",
            base_url="https://api.moonshot.cn/v1",
        )

        # 系统提示，要求Kimi分析代码
        system_prompt = """
        你是月之暗面（Kimi）的智能客服，你负责分析用户上传的代码。请对代码实现功能进行简要概括。

        请使用如下 JSON 格式输出你的回复：
        {
            "text": "代码分析结果"
        }

        注意：
        1. 只能返回 `text` 字段，不能包含 `image` 或 `url` 字段。
        2. `text` 字段中只能包含文字信息。
        """

        # 调用 API 生成代码分析
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_code}
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        # 提取分析结果
        answer = completion.choices[0].message.content
        answer_json = json.loads(answer)  # 将返回的JSON字符串解析为字典

        # 确保返回的格式符合要求
        result = {
            "data": "000",
            "text": answer_json.get("text", "无法获取代码分析结果")
        }

        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")  # 记录错误日志

        # 检查是否是网络问题或链接解析失败
        if "base_url" in str(e) or "网络" in str(e):
            return jsonify({
                "data": "001",
                "text": "服务器繁忙，解析链接时遇到问题。请检查链接的合法性，或稍后重试。"
            }), 500
        else:
            return jsonify({
                "data": "001",
                "text": "服务器繁忙，请稍后再试。"
            }), 500

# 发送邮件功能
# @app.route('/send-sms', methods=['POST'])
# def send_sms():
#     pass

# 查询老师的所有作业
@app.route('/api/queryTeacherJob', methods=['POST'])
def queryTeacherJob():
    try:
        # 建立连接
        connection = mysql.connector.connect(
            host='localhost',  # 数据库服务器地址
            port=23306,  # 数据库端口
            user='root',  # 数据库用户名
            password='123456',  # 数据库密码
            database='code_manage_system'  # 数据库名称
        )

        if connection.is_connected():
            print("数据库连接成功！")
            # 获取数据库服务器信息
            db_info = connection.get_server_info()
            print(f"连接到 MySQL 数据库，版本: {db_info}")

            # 创建游标对象
            cursor = connection.cursor()

            # 获取 POST 请求中的 JSON 数据
            data = request.json

            # 获取 teacher_id
            teacher_id = data.get('teacher_id')
            if not teacher_id:  # 检查是否为空
                return jsonify({
                    "code": "001",
                    "info": "请输入教师id",
                    "data": []
                }), 400

            # 执行 SQL 查询
            query = """
            SELECT job_id, title, content, course_id, class_id, status, start_time, end_time
            FROM job 
            WHERE class_id IN (
                SELECT class_id 
                FROM class 
                WHERE teacher_id = %s
            )
            """
            cursor.execute(query, (teacher_id,))
            records = cursor.fetchall()

            # 检查查询结果是否为空
            if not records:
                return jsonify({
                    "code": "001",
                    "info": "该教师没有课程",
                    "data": []
                }), 404

            # 将查询结果转换为字典列表
            result = []
            for row in records:
                job_data = {
                    "jobId": row[0],
                    "title": row[1],
                    "content": row[2],
                    "courseId": row[3],
                    "classId": row[4],
                    "status": row[5],
                    "startTime": row[6].isoformat() + "Z" if row[6] else None,
                    "endTime": row[7].isoformat() + "Z" if row[7] else None
                }
                result.append(job_data)

            print("查询结果：", result)

            # 返回 JSON 格式的查询结果
            return jsonify({
                "code": "000",
                "info": "操作成功",
                "data": result
            })

    except Error as e:
        print(f"连接数据库时发生错误: {e}")
        return jsonify({
            "code": "001",
            "info": str(e),
            "data": []
        }), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭。")

# 查询某个作业的提交人数/未提交人数
@app.route('/api/queryJobCommitRate', methods=['POST'])
def queryJobCommitRate():
    try:
        # 获取请求中的数据
        data = request.json
        job_id = data.get("job_id", "").strip()

        if not job_id:
            return jsonify({"code": "001", "info": "job_id不能为空", "submitted": 0})

        # 建立数据库连接
        connection = mysql.connector.connect(
            host='localhost',  # 数据库服务器地址
            port=23306,  # 数据库端口
            user='root',  # 数据库用户名
            password='123456',  # 数据库密码
            database='code_manage_system'  # 数据库名称
        )

        # 创建游标
        cursor = connection.cursor(dictionary=True)

        # 查询指定 job_id 的提交人数
        query = "SELECT COUNT(*) AS submitted FROM student_job WHERE job_id = %s AND status = 'submitted'"
        cursor.execute(query, (job_id,))
        result = cursor.fetchone()

        # 关闭游标和连接
        cursor.close()
        connection.close()

        if result:
            return jsonify({"code": "000", "info": "操作成功", "submitted": result['submitted']})
        else:
            return jsonify({"code": "001", "info": "未找到数据", "submitted": 0})

    except mysql.connector.Error as err:
        return jsonify({"code": "001", "info": f"数据库错误: {err}", "submitted": 0})
    except Exception as e:
        return jsonify({"code": "001", "info": f"发生错误: {e}", "submitted": 0})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088)