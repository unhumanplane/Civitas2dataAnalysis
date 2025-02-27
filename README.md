# Civitas 数据分析工具

这个项目是为Civitas游戏设计的数据收集和可视化工具。它能够自动收集游戏中的用户状态、技能以及详细信息，并提供直观的数据可视化界面。

## 功能特点

- 自动收集并存储用户状态数据
- 自动收集并存储用户技能数据
- 自动收集并存储用户详细信息
- 提供直观的表格格式数据可视化
- 支持用户名搜索和数据筛选
- 实时数据更新和刷新

## 项目结构

- `civitas_status_skill.user.js` - Tampermonkey脚本，用于从游戏中收集数据
- `consolidated_data_server.py` - 主服务器，用于接收和存储数据并提供Web界面
- `visualization.js` - 前端可视化脚本
- `visualization.css` - 前端样式表
- `visualization.html` - 前端HTML页面

## 安装与使用

### 服务器端

1. 安装Python依赖：
```
pip install -r requirements.txt
```

2. 启动服务器：
```
python consolidated_data_server.py
```

服务器默认运行在 `http://localhost:5000`

### 客户端

1. 安装Tampermonkey浏览器扩展
2. 导入`civitas_status_skill.user.js`脚本
3. 访问Civitas游戏页面，脚本将自动运行并收集数据

### 可视化界面

访问 `http://localhost:5000/visualization/` 查看数据可视化页面。

## API接口

- `/api/record_status` - 记录用户状态数据
- `/api/record_skill` - 记录用户技能数据
- `/api/record_userdetail` - 记录用户详细信息
- `/api/data` - 获取整合的数据
- `/api/stats` - 获取数据统计信息
- `/api/user_detail` - 获取用户详细信息

## 项目目的

该项目旨在分析Civitas2游戏数据，提供数据洞察和可视化，帮助玩家更好地了解游戏进程和优化游戏策略。

## 开发与贡献

欢迎提出问题和建议，也欢迎贡献代码。
