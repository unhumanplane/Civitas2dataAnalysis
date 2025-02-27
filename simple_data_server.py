import http.server
import json
import os
import datetime
import logging
from urllib.parse import urlparse, parse_qs

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建数据存储目录
DATA_DIR = "civitas_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"创建数据目录: {DATA_DIR}")

class CivitasDataHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/json', status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # 允许所有来源的跨域请求
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """处理 OPTIONS 请求，支持 CORS 预检请求"""
        self._set_headers()
        
    def do_GET(self):
        """处理 GET 请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            self._serve_home_page()
        elif path == '/api/list_records':
            self._list_records()
        elif path.startswith('/api/get_record/'):
            filename = path.split('/api/get_record/')[1]
            self._get_record(filename)
        elif path == '/api/stats':
            self._get_stats()
        else:
            self._set_headers(status_code=404)
            self.wfile.write(json.dumps({"status": 0, "message": "Not found"}).encode())
    
    def do_POST(self):
        """处理 POST 请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/api/record_status':
                self._record_status(data)
            elif self.path == '/api/record_skill':
                self._record_skill(data)
            else:
                self._set_headers(status_code=404)
                self.wfile.write(json.dumps({"status": 0, "message": "Not found"}).encode())
        except json.JSONDecodeError:
            self._set_headers(status_code=400)
            self.wfile.write(json.dumps({"status": 0, "message": "Invalid JSON"}).encode())
        except Exception as e:
            logger.error(f"处理请求时发生错误: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Server error: {str(e)}"}).encode())
    
    def _serve_home_page(self):
        """提供主页 HTML"""
        html = """
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
        self._set_headers(content_type='text/html')
        self.wfile.write(html.encode())
    
    def _record_status(self, data):
        """记录状态数据"""
        try:
            if not data:
                self._set_headers(status_code=400)
                self.wfile.write(json.dumps({"status": 0, "message": "No data provided"}).encode())
                return
            
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
            
            logger.info(f"状态数据已记录: {status_file}")
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "message": "Status data recorded successfully"}).encode())
        
        except Exception as e:
            logger.error(f"记录状态数据时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error recording status data: {str(e)}"}).encode())
    
    def _record_skill(self, data):
        """记录技能数据"""
        try:
            if not data:
                self._set_headers(status_code=400)
                self.wfile.write(json.dumps({"status": 0, "message": "No data provided"}).encode())
                return
            
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
            
            logger.info(f"技能数据已记录: {skill_file}")
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "message": "Skill data recorded successfully"}).encode())
        
        except Exception as e:
            logger.error(f"记录技能数据时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error recording skill data: {str(e)}"}).encode())
    
    def _list_records(self):
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
            
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "data": records}).encode())
        
        except Exception as e:
            logger.error(f"列出记录时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error listing records: {str(e)}"}).encode())
    
    def _get_record(self, filename):
        """获取特定记录的内容"""
        try:
            file_path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(file_path):
                self._set_headers(status_code=404)
                self.wfile.write(json.dumps({"status": 0, "message": "Record not found"}).encode())
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "data": data}).encode())
        
        except Exception as e:
            logger.error(f"获取记录时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error getting record: {str(e)}"}).encode())
    
    def _get_stats(self):
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
            
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": 1, 
                "data": {
                    "total_users": len(users),
                    "users": list(users),
                    "status_records": status_records,
                    "skill_records": skill_records,
                    "total_records": status_records + skill_records
                }
            }).encode())
        
        except Exception as e:
            logger.error(f"获取统计信息时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error getting stats: {str(e)}"}).encode())

def run_server(host='0.0.0.0', port=5000):
    """运行服务器"""
    server_address = (host, port)
    httpd = http.server.HTTPServer(server_address, CivitasDataHandler)
    logger.info(f"Civitas 数据服务器启动在 http://{host}:{port}")
    logger.info(f"数据将被保存到 {os.path.abspath(DATA_DIR)} 目录")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
