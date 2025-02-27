import http.server
import json
import os
import datetime
import logging
import shutil
from urllib.parse import urlparse, parse_qs

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据文件路径
DATA_DIR = "civitas_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"创建数据目录: {DATA_DIR}")

CONSOLIDATED_DATA_FILE = os.path.join(DATA_DIR, "consolidated_data.json")
VISUALIZATION_DIR = "visualization"  # 修改可视化目录为项目根目录下的visualization文件夹

if not os.path.exists(VISUALIZATION_DIR):
    os.makedirs(VISUALIZATION_DIR)
    logger.info(f"创建可视化目录: {VISUALIZATION_DIR}")

# 初始化整合数据文件
def init_consolidated_data():
    if not os.path.exists(CONSOLIDATED_DATA_FILE):
        with open(CONSOLIDATED_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "status": {},
                "skills": {},
                "userdetail": {},
                "history": [],
                "last_updated": datetime.datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        logger.info(f"创建整合数据文件: {CONSOLIDATED_DATA_FILE}")
    
    # 将可视化文件复制到visualization目录
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 复制HTML文件
        html_src = os.path.join(script_dir, "visualization.html")
        html_dest = os.path.join(VISUALIZATION_DIR, "index.html")
        if os.path.exists(html_src):
            shutil.copyfile(html_src, html_dest)
            logger.info(f"已复制HTML文件: {html_src} -> {html_dest}")
        else:
            logger.error(f"HTML文件不存在: {html_src}")
            
        # 复制JavaScript文件
        js_src = os.path.join(script_dir, "visualization.js")
        js_dest = os.path.join(VISUALIZATION_DIR, "visualization.js")
        if os.path.exists(js_src):
            shutil.copyfile(js_src, js_dest)
            logger.info(f"已复制JS文件: {js_src} -> {js_dest}")
        else:
            logger.error(f"JS文件不存在: {js_src}")
            
        # 复制CSS文件
        css_src = os.path.join(script_dir, "visualization.css")
        css_dest = os.path.join(VISUALIZATION_DIR, "visualization.css")
        if os.path.exists(css_src):
            shutil.copyfile(css_src, css_dest)
            logger.info(f"已复制CSS文件: {css_src} -> {css_dest}")
        else:
            logger.error(f"CSS文件不存在: {css_src}")
        
        logger.info("可视化文件已复制到visualization目录")
    except Exception as e:
        logger.error(f"复制可视化文件时出错: {str(e)}")

# 加载整合数据
def load_consolidated_data():
    if os.path.exists(CONSOLIDATED_DATA_FILE):
        try:
            with open(CONSOLIDATED_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保userdetail字段存在
                if "userdetail" not in data:
                    data["userdetail"] = {}
                return data
        except Exception as e:
            logger.error(f"加载整合数据文件时出错: {str(e)}")
            return {
                "status": {},
                "skills": {},
                "userdetail": {},
                "history": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
    else:
        return {
            "status": {},
            "skills": {},
            "userdetail": {},
            "history": [],
            "last_updated": datetime.datetime.now().isoformat()
        }

# 保存整合数据
def save_consolidated_data(data):
    with open(CONSOLIDATED_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
        
        logger.info(f"收到GET请求: {path}")
        
        # 检查是否是请求静态文件
        if path == '/visualization/':
            # 直接提供可视化页面的index.html
            self._serve_static_file('index.html')
            return
        elif path.startswith('/visualization/'):
            # 提供其他静态文件
            file_path = path.split('/visualization/')[1]
            if file_path:  # 确保不是空字符串
                self._serve_static_file(file_path)
                return
            else:
                # 如果是/visualization/后面没有内容，也提供index.html
                self._serve_static_file('index.html')
                return
        
        if path == '/':
            self._serve_home_page()
        elif path == '/visualization':
            self._redirect_to('/visualization/')
        elif path == '/api/data':
            self._get_consolidated_data()
        elif path.startswith('/api/get_record/'):
            filename = path.split('/api/get_record/')[1]
            self._get_record(filename)
        elif path == '/api/stats':
            self._get_stats()
        elif path == '/api/user_detail':
            self._get_user_detail()
        else:
            logger.warning(f"未找到路径: {path}")
            self._set_headers(status_code=404)
            self.wfile.write(json.dumps({"status": 0, "message": "Not found"}).encode())
    
    def _redirect_to(self, url):
        """重定向到指定URL"""
        self.send_response(302)
        self.send_header('Location', url)
        self.end_headers()
    
    def _serve_static_file(self, file_path):
        """提供静态文件"""
        logger.info(f"尝试提供静态文件: {file_path}")
        full_path = os.path.join(VISUALIZATION_DIR, file_path)
        logger.info(f"完整文件路径: {full_path}")
        
        if not os.path.exists(full_path):
            logger.error(f"文件不存在: {full_path}")
            self._set_headers(status_code=404)
            self.wfile.write(b"File not found")
            return
        
        if os.path.isdir(full_path):
            logger.error(f"请求的是目录而非文件: {full_path}")
            self._set_headers(status_code=404)
            self.wfile.write(b"File not found (is a directory)")
            return
        
        # 设置合适的内容类型
        content_type = 'text/plain'
        if file_path.endswith('.html'):
            content_type = 'text/html'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.json'):
            content_type = 'application/json'
        
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            logger.info(f"成功读取文件: {full_path} (大小: {len(content)} 字节)")
            self._set_headers(content_type=content_type)
            self.wfile.write(content)
            logger.info(f"成功提供文件: {full_path}")
        except Exception as e:
            logger.error(f"提供静态文件时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(b"Server error")
    
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
            elif self.path == '/api/record_userdetail':
                self._record_userdetail(data)
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
                    .button { display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; 
                             text-decoration: none; border-radius: 5px; margin-top: 20px; }
                    code { background: #eee; padding: 2px 5px; border-radius: 3px; }
                </style>
            </head>
            <body>
                <h1>Civitas 数据服务器</h1>
                <p>这是一个用于记录 Civitas 游戏数据的 API 服务器。</p>
                
                <a href="/visualization/" class="button">查看数据可视化</a>
                
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
                    <p><span class="method">POST</span> /api/record_userdetail</p>
                    <p>记录用户详细信息</p>
                </div>
                
                <div class="endpoint">
                    <p><span class="method">GET</span> /api/data</p>
                    <p>获取整合后的数据</p>
                </div>
                
                <div class="endpoint">
                    <p><span class="method">GET</span> /api/stats</p>
                    <p>获取数据统计信息</p>
                </div>
                
                <div class="endpoint">
                    <p><span class="method">GET</span> /api/user_detail</p>
                    <p>获取用户详细信息</p>
                </div>
            </body>
        </html>
        """
        self._set_headers(content_type='text/html')
        self.wfile.write(html.encode())
    
    def _serve_visualization(self):
        """提供可视化页面"""
        logger.info(f"请求可视化页面，尝试提供: {os.path.join(VISUALIZATION_DIR, 'index.html')}")
        visualization_file = os.path.join(VISUALIZATION_DIR, "index.html")
        
        if not os.path.exists(visualization_file):
            logger.error(f"可视化文件不存在: {visualization_file}")
            self._set_headers(content_type='text/html')
            self.wfile.write("""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>可视化页面不存在</h1>
                    <p>请确保visualization/index.html已正确创建。</p>
                </body>
            </html>
            """.encode())
            return
        
        try:
            logger.info(f"正在读取文件: {visualization_file}")
            with open(visualization_file, 'rb') as f:
                content = f.read()
            self._set_headers(content_type='text/html')
            self.wfile.write(content)
            logger.info(f"成功提供可视化页面: {visualization_file}")
        except Exception as e:
            logger.error(f"提供可视化页面时出错: {str(e)}")
            self._set_headers(content_type='text/html', status_code=500)
            self.wfile.write(f"""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>服务器错误</h1>
                    <p>{str(e)}</p>
                </body>
            </html>
            """.encode())
    
    def _record_status(self, data):
        """记录状态数据"""
        try:
            if not data:
                self._set_headers(status_code=400)
                self.wfile.write(json.dumps({"status": 0, "message": "No data provided"}).encode())
                return
            
            # 确保有基本信息
            username = data.get('username', 'unknown')
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            
            # 加载整合数据
            consolidated_data = load_consolidated_data()
            
            # 更新状态数据
            consolidated_data["status"][username] = {
                "data": data.get("data", {}),
                "timestamp": timestamp
            }
            
            # 添加历史记录
            history_entry = {
                "type": "status",
                "username": username,
                "timestamp": timestamp,
                "data": data.get("data", {})
            }
            consolidated_data["history"].append(history_entry)
            
            # 限制历史记录长度
            if len(consolidated_data["history"]) > 1000:
                consolidated_data["history"] = consolidated_data["history"][-1000:]
            
            # 更新时间
            consolidated_data["last_updated"] = datetime.datetime.now().isoformat()
            
            # 保存更新后的数据
            save_consolidated_data(consolidated_data)
            
            logger.info(f"状态数据已记录: {username}")
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
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            
            # 加载整合数据
            consolidated_data = load_consolidated_data()
            
            # 更新技能数据
            consolidated_data["skills"][username] = {
                "data": data.get("data", {}),
                "timestamp": timestamp
            }
            
            # 添加历史记录
            history_entry = {
                "type": "skill",
                "username": username,
                "timestamp": timestamp,
                "data": data.get("data", {})
            }
            consolidated_data["history"].append(history_entry)
            
            # 限制历史记录长度
            if len(consolidated_data["history"]) > 1000:
                consolidated_data["history"] = consolidated_data["history"][-1000:]
            
            # 更新时间
            consolidated_data["last_updated"] = datetime.datetime.now().isoformat()
            
            # 保存更新后的数据
            save_consolidated_data(consolidated_data)
            
            logger.info(f"技能数据已记录: {username}")
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "message": "Skill data recorded successfully"}).encode())
        
        except Exception as e:
            logger.error(f"记录技能数据时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error recording skill data: {str(e)}"}).encode())
    
    def _record_userdetail(self, data):
        """记录用户详细信息"""
        try:
            if not data:
                self._set_headers(status_code=400)
                self.wfile.write(json.dumps({"status": 0, "message": "No data provided"}).encode())
                return
            
            # 确保有基本信息
            username = data.get('username', 'unknown')
            timestamp = data.get('timestamp', datetime.datetime.now().isoformat())
            
            # 加载整合数据
            consolidated_data = load_consolidated_data()
            
            # 更新用户详细信息
            consolidated_data["userdetail"][username] = {
                "data": data,
                "timestamp": timestamp
            }
            
            # 添加历史记录
            history_entry = {
                "type": "userdetail",
                "username": username,
                "timestamp": timestamp,
                "data": data
            }
            consolidated_data["history"].append(history_entry)
            
            # 限制历史记录长度
            if len(consolidated_data["history"]) > 1000:
                consolidated_data["history"] = consolidated_data["history"][-1000:]
            
            # 更新时间
            consolidated_data["last_updated"] = datetime.datetime.now().isoformat()
            
            # 保存更新后的数据
            save_consolidated_data(consolidated_data)
            
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "message": "User detail recorded successfully"}).encode())
            
        except Exception as e:
            logger.error(f"记录用户详细信息时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error recording user detail: {str(e)}"}).encode())
    
    def _get_consolidated_data(self):
        """获取整合的数据"""
        try:
            consolidated_data = load_consolidated_data()
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "data": consolidated_data}).encode())
        except Exception as e:
            logger.error(f"获取整合数据时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error getting consolidated data: {str(e)}"}).encode())
    
    def _get_stats(self):
        """获取统计信息"""
        try:
            consolidated_data = load_consolidated_data()
            
            status_users = list(consolidated_data["status"].keys())
            skill_users = list(consolidated_data["skills"].keys())
            userdetail_users = list(consolidated_data["userdetail"].keys())
            all_users = list(set(status_users + skill_users + userdetail_users))
            
            stats = {
                "total_users": len(all_users),
                "users": all_users,
                "status_records": len(status_users),
                "skill_records": len(skill_users),
                "userdetail_records": len(userdetail_users),
                "history_records": len(consolidated_data["history"]),
                "last_updated": consolidated_data["last_updated"]
            }
            
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "data": stats}).encode())
        
        except Exception as e:
            logger.error(f"获取统计信息时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error getting stats: {str(e)}"}).encode())

    def _get_user_detail(self):
        """获取用户详细信息"""
        try:
            consolidated_data = load_consolidated_data()
            
            self._set_headers()
            self.wfile.write(json.dumps({"status": 1, "data": consolidated_data["userdetail"]}).encode())
        except Exception as e:
            logger.error(f"获取用户详细信息时出错: {str(e)}")
            self._set_headers(status_code=500)
            self.wfile.write(json.dumps({"status": 0, "message": f"Error getting user detail: {str(e)}"}).encode())

def run_server(host='0.0.0.0', port=5000):
    """运行服务器"""
    # 初始化整合数据文件
    init_consolidated_data()
    
    server_address = (host, port)
    httpd = http.server.HTTPServer(server_address, CivitasDataHandler)
    logger.info(f"Civitas 数据服务器启动在 http://{host}:{port}")
    logger.info(f"数据可视化页面地址: http://{host}:{port}/visualization/")
    logger.info(f"整合数据保存在: {os.path.abspath(CONSOLIDATED_DATA_FILE)}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
