import os
import json
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from markupsafe import escape  # Using markupsafe instead of jinja2 for escape

app = Flask(__name__)
CORS(app)  # 启用CORS，允许油猴脚本跨域请求

# 创建数据存储目录
DATA_DIR = "civitas_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/api/record_status', methods=['POST'])
def record_status():
    """记录状态数据"""
    try:
        data = request.json
        if not data:
            return jsonify({"status": 0, "message": "No data provided"}), 400
        
        # 确保有基本信息
        username = data.get('username', 'unknown')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 记录状态信息
        status_file = os.path.join(DATA_DIR, f"status_{username}_{timestamp}.json")
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新最新状态文件
        latest_status_file = os.path.join(DATA_DIR, f"status_{username}_latest.json")
        with open(latest_status_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"状态数据已记录: {status_file}")
        return jsonify({"status": 1, "message": "Status data recorded successfully"})
    
    except Exception as e:
        print(f"记录状态数据时出错: {str(e)}")
        return jsonify({"status": 0, "message": f"Error recording status data: {str(e)}"}), 500

@app.route('/api/record_skill', methods=['POST'])
def record_skill():
    """记录技能数据"""
    try:
        data = request.json
        if not data:
            return jsonify({"status": 0, "message": "No data provided"}), 400
        
        # 确保有基本信息
        username = data.get('username', 'unknown')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 记录技能信息
        skill_file = os.path.join(DATA_DIR, f"skill_{username}_{timestamp}.json")
        with open(skill_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新最新技能文件
        latest_skill_file = os.path.join(DATA_DIR, f"skill_{username}_latest.json")
        with open(latest_skill_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"技能数据已记录: {skill_file}")
        return jsonify({"status": 1, "message": "Skill data recorded successfully"})
    
    except Exception as e:
        print(f"记录技能数据时出错: {str(e)}")
        return jsonify({"status": 0, "message": f"Error recording skill data: {str(e)}"}), 500

@app.route('/api/list_records', methods=['GET'])
def list_records():
    """列出所有记录"""
    try:
        records = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".json") and not filename.endswith("_latest.json"):
                file_path = os.path.join(DATA_DIR, filename)
                stat = os.stat(file_path)
                records.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        # 按时间排序，最新的在前
        records.sort(key=lambda x: x["created"], reverse=True)
        
        return jsonify({"status": 1, "data": records})
    
    except Exception as e:
        print(f"列出记录时出错: {str(e)}")
        return jsonify({"status": 0, "message": f"Error listing records: {str(e)}"}), 500

@app.route('/api/get_record/<filename>', methods=['GET'])
def get_record(filename):
    """获取特定记录的内容"""
    try:
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"status": 0, "message": "Record not found"}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({"status": 1, "data": data})
    
    except Exception as e:
        print(f"获取记录时出错: {str(e)}")
        return jsonify({"status": 0, "message": f"Error getting record: {str(e)}"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    try:
        # 找出所有用户
        users = set()
        status_records = 0
        skill_records = 0
        
        for filename in os.listdir(DATA_DIR):
            if not filename.endswith("_latest.json"):
                parts = filename.split('_')
                if len(parts) >= 2:
                    record_type = parts[0]
                    username = parts[1]
                    users.add(username)
                    
                    if record_type == "status":
                        status_records += 1
                    elif record_type == "skill":
                        skill_records += 1
        
        return jsonify({
            "status": 1, 
            "data": {
                "total_users": len(users),
                "users": list(users),
                "status_records": status_records,
                "skill_records": skill_records,
                "total_records": status_records + skill_records
            }
        })
    
    except Exception as e:
        print(f"获取统计信息时出错: {str(e)}")
        return jsonify({"status": 0, "message": f"Error getting stats: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    """主页 - 显示简单的API信息"""
    return """
    <html>
        <head>
            <title>Civitas Data Server</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                .endpoint { background: #f4f4f4; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
                .method { font-weight: bold; color: #0066cc; }
                code { background: #eee; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Civitas 数据服务器</h1>
            <p>这是一个用于记录 Civitas 游戏数据的 API 服务器。</p>
            
            <h2>可用的 API 端点:</h2>
            
            <div class="endpoint">
                <p><span class="method">POST</span> /api/record_status</p>
                <p>记录角色状态数据</p>
            </div>
            
            <div class="endpoint">
                <p><span class="method">POST</span> /api/record_skill</p>
                <p>记录角色技能数据</p>
            </div>
            
            <div class="endpoint">
                <p><span class="method">GET</span> /api/list_records</p>
                <p>列出所有记录的数据文件</p>
            </div>
            
            <div class="endpoint">
                <p><span class="method">GET</span> /api/get_record/:filename</p>
                <p>获取特定记录的内容</p>
            </div>
            
            <div class="endpoint">
                <p><span class="method">GET</span> /api/stats</p>
                <p>获取数据统计信息</p>
            </div>
        </body>
    </html>
    """

if __name__ == '__main__':
    print(f"Civitas 数据服务器启动中...")
    print(f"数据将被保存到 {os.path.abspath(DATA_DIR)} 目录")
    app.run(host='0.0.0.0', port=5000, debug=True)
