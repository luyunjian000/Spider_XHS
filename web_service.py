# web_service.py
from flask import Flask, request, jsonify, send_file
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from main import Data_Spider, init
import os
import threading

app = Flask(__name__)
auth = HTTPBasicAuth()

# Basic Auth 配置（修改为您的凭证）
users = {
    "admin": generate_password_hash("lyj11012012580")  # 用户名: admin 密码: secretpass
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# 初始化爬虫
cookies_str, base_path = init()
data_spider = Data_Spider()

@app.route('/api/search/notes', methods=['POST'])
@auth.login_required
def search_notes():
    """
    执行搜索爬虫任务
    请求示例：
    {
        "query": "榴莲",
        "num": 1,
        "sort": "general",
        "note_type": 2,
        "save_choice": "all"
    }
    """
    data = request.json
    required_fields = ['query', 'num']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # 启动异步任务
    # def async_task():
    #     data_spider.spider_some_search_note(
    #         query=data['query'],
    #         require_num=data['num'],
    #         cookies_str=cookies_str,
    #         base_path=base_path,
    #         save_choice=data.get('save_choice', 'all'),
    #         sort=data.get('sort', 'general'),
    #         note_type=data.get('note_type', 0)
    #     )

    # threading.Thread(target=async_task).start()
    
    # return jsonify({
    #     "status": "started",
    #     "result_path": f"/download/{data['query']}.xlsx",
    #     "message": "Task is running in background"
    # })

    
    # 同步执行爬虫任务
    note_list, note_detail_list, success, msg = data_spider.query_some_search_note(
        query=data['query'],
        require_num=data['num'],
        cookies_str=cookies_str,
        sort=data.get('sort', 'general'),
        note_type=data.get('note_type', 0)
    )

    return jsonify({
        "success": success,
        "note_list": note_list,
        "note_detail_list": note_detail_list,
        "message": str(msg)
    })


@app.route('/api/search/user/nodes', methods=['POST'])
@auth.login_required
def search_user_notes():
    """
    执行搜索爬虫任务
    请求示例：
    {
        "user_query": ["95359404796", "119748158"], 小红书号就行，搜出来是唯一的
        "node_count": 2 // 获取返回的前2个笔记
    }
    """
    data = request.json
    required_fields = ['user_query', 'node_count']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # 同步执行爬虫任务
    success, msg, note_list, note_detail_list = data_spider.query_user_notes(
        user_query=data['user_query'],
        node_count=data['node_count'],
        cookies_str=cookies_str
    )

    return jsonify({
        "success": success,
        "note_list": note_list,
        "note_detail_list": note_detail_list,
        "message": str(msg)
    })


@app.route('/download/<filename>')
@auth.login_required
def download_file(filename):
    """下载结果文件"""
    file_path = os.path.join(base_path['excel'], filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11012, threaded=True)