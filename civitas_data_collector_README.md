# Civitas 数据收集系统

这是一个用于收集和记录 Civitas 游戏角色状态和技能数据的系统。它由两部分组成：

1. 油猴脚本 (`civitas_status_skill.user.js`): 在游戏网页上运行，读取角色数据并发送到后端服务器
2. 后端服务器 (`simple_data_server.py`): 接收并存储油猴脚本发送的数据

## 系统功能

- 自动收集角色状态数据（精力、健康、快乐、饥饿度）
- 自动收集角色技能数据（技能等级、技能值、小技能等）
- 将数据存储到本地文件系统
- 提供简单的 API 接口查询历史数据和统计信息

## 安装和使用方法

### 1. 安装油猴脚本

1. 确保浏览器已安装 Tampermonkey 浏览器扩展
2. 在 Tampermonkey 中新建脚本，将 `civitas_status_skill.user.js` 的内容复制粘贴进去
3. 保存脚本

### 2. 启动后端服务器

1. 确保安装了 Python 3.6+
2. 在命令行中运行：
   ```
   python simple_data_server.py
   ```
3. 服务器将启动，默认监听 0.0.0.0:5000

### 3. 使用方法

1. 打开 Civitas 游戏网站 (https://civitas2.top/)
2. 登录游戏
3. 页面右上角会出现两个按钮：
   - 「显示状态和技能」：在浏览器控制台显示当前角色状态和技能信息
   - 「发送数据到服务器」：将当前角色状态和技能信息发送到后端服务器记录

### 4. 查看记录的数据

服务器启动后，可以通过浏览器访问以下 URL：

- `http://localhost:5000/`：主页，显示 API 接口信息
- `http://localhost:5000/api/list_records`：列出所有记录
- `http://localhost:5000/api/stats`：显示数据统计信息
- `http://localhost:5000/api/get_record/{文件名}`：获取特定记录内容

数据文件保存在 `civitas_data` 目录下，格式为 JSON，文件名包含数据类型、用户名和时间戳。

## 注意事项

1. 本系统默认配置为连接本地服务器 (`localhost:5000`)，如需连接远程服务器，请修改油猴脚本中的 `SERVER_URL` 变量
2. 如需在公网环境使用此系统，请考虑添加合适的身份验证和授权机制
3. 服务器使用简单的 HTTP 服务，不适合生产环境使用，请根据需要增强安全性

## 服务器 API 端点

| 方法 | 端点 | 说明 |
| ---- | ---- | ---- |
| POST | /api/record_status | 记录角色状态数据 |
| POST | /api/record_skill | 记录角色技能数据 |
| GET | /api/list_records | 列出所有记录 |
| GET | /api/get_record/{filename} | 获取特定记录内容 |
| GET | /api/stats | 获取数据统计信息 |

## 数据存储格式

数据以 JSON 格式存储在文件中，文件命名方式：

- 状态数据：`status_{用户名}_{时间戳}.json`
- 技能数据：`skill_{用户名}_{时间戳}.json`
- 最新状态：`status_{用户名}_latest.json`
- 最新技能：`skill_{用户名}_latest.json`
